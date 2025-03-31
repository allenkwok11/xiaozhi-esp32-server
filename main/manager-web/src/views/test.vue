<template>
  <div class="container">
    <h1 class="title">XiaoZhi ESP32 Server 测试助手</h1>
    <div class="chat-container" ref="chatContainer">
      <div v-for="(message, index) in messages" :key="index"
           :class="['message', message.role === 'user' ? 'user' : 'assistant']">
        <span>{{ message.content }}</span>
      </div>
    </div>
    <div class="controls">
      <button @click="toggleRecording" :disabled="wsStatus !== 'connected'"
              :class="{ recording: isRecording }">
        {{ isRecording ? '停止录音' : '开始录音' }}
      </button>
      <p>WebSocket: {{ wsStatus }}</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import Recorder from 'opus-recorder';
import { OpusDecoder } from 'opus-decoder';

export default {
  name: 'TestPage',
  setup() {
    const messages = ref([]);
    const chatContainer = ref(null);
    const wsStatus = ref('disconnected');
    const isRecording = ref(false);
    let ws = null;
    let recorder = null;
    let stream = null;
    let audioContext = null;
    let sourceNode = null;
    let audioDecoder = null;
    let audioBufferQueue = []; // 当前句子的音频缓冲区
    let playbackQueue = []; // 播放队列，存储待播放的句子
    let isPlaying = false;

    const connectWebSocket = () => {
      ws = new WebSocket('ws://192.168.3.97:8000');//修改服务端地址
      ws.binaryType = 'arraybuffer';
      ws.onopen = () => {
        wsStatus.value = 'connected';
        console.log('WebSocket 连接成功');
        ws.send(JSON.stringify({ type: 'auth', 'device-id': 'test-device' }));
        audioDecoder = new OpusDecoder({ sampleRate: 16000, channels: 1 });
      };
      ws.onmessage = async (event) => {
        if (typeof event.data === 'string') {
          const msg = JSON.parse(event.data);
          console.log('收到文本消息:', msg);

          if (msg.type === 'stt') {
            messages.value.push({ role: 'user', content: msg.text });
            scrollToBottom();
          } else if (msg.type === 'llm') {
            messages.value.push({ role: 'assistant', content: msg.text });
            scrollToBottom();
          } else if (msg.type === 'tts') {
            if (msg.state === 'sentence_start') {
              // 开始新句子，清空当前缓冲区
              audioBufferQueue = [];
              const lastMessage = messages.value[messages.value.length - 1];
              if (!lastMessage || lastMessage.content !== msg.text) {
                messages.value.push({ role: 'assistant', content: msg.text });
                scrollToBottom();
              }
            } else if (msg.state === 'sentence_end') {
              // 句子结束，将当前缓冲区加入播放队列
              if (audioBufferQueue.length > 0) {
                playbackQueue.push([...audioBufferQueue]);
                audioBufferQueue = [];
                playNextInQueue(); // 尝试播放队列中的下一句
              }
            } else if (msg.state === 'stop') {
              console.log('TTS 任务结束');
              // 确保所有剩余音频播放
              if (audioBufferQueue.length > 0) {
                playbackQueue.push([...audioBufferQueue]);
                audioBufferQueue = [];
                playNextInQueue();
              }
            }
          } else if (msg.type === 'hello') {
            console.log('收到服务器初始化消息:', msg);
          }
        } else if (event.data instanceof ArrayBuffer) {
          console.log('收到音频帧，大小:', event.data.byteLength, '字节');
          const opusFrame = new Uint8Array(event.data);
          const frameHead = Array.from(opusFrame.slice(0, 8))
              .map(b => b.toString(16).padStart(2, '0'))
              .join(' ');
          console.log('音频帧前8字节:', frameHead);

          try {
            const decoded = audioDecoder.decodeFrame(opusFrame);
            console.log('解码结果:', decoded);
            if (decoded && decoded.channelData && decoded.channelData[0]) {
              const pcmData = decoded.channelData[0];
              if (pcmData.length > 0) {
                audioBufferQueue.push(pcmData);
                console.log('解码音频帧，PCM 数据长度:', pcmData.length);
                // 如果缓冲区达到一定长度（例如 5 帧，180ms），立即播放
                if (audioBufferQueue.length >= 5 && playbackQueue.length === 0 && !isPlaying) {
                  playbackQueue.push([...audioBufferQueue]);
                  audioBufferQueue = [];
                  playNextInQueue();
                }
              } else {
                console.warn('解码成功，但 PCM 数据长度为 0');
              }
            } else {
              console.warn('解码结果无效:', decoded);
            }
          } catch (e) {
            console.error('Opus 解码错误:', e);
          }
        }
      };
      ws.onerror = (error) => {
        console.error('WebSocket 错误:', error);
        wsStatus.value = 'error';
      };
      ws.onclose = () => {
        wsStatus.value = 'disconnected';
        console.log('WebSocket 断开');
        setTimeout(connectWebSocket, 1000);
      };
    };

    const scrollToBottom = () => {
      nextTick(() => {
        if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
      });
    };

    const playNextInQueue = async () => {
      if (isPlaying || playbackQueue.length === 0) {
        return; // 正在播放或队列为空，等待下次触发
      }
      isPlaying = true;

      if (!audioContext || audioContext.state === 'closed') {
        audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
      }

      const pcmBuffers = playbackQueue.shift(); // 取出队列中的第一句
      const totalLength = pcmBuffers.reduce((sum, pcm) => sum + pcm.length, 0);
      if (totalLength === 0) {
        console.error('音频缓冲区总长度为 0，无法播放');
        isPlaying = false;
        playNextInQueue(); // 尝试播放下一句
        return;
      }

      const mergedPcm = new Float32Array(totalLength);
      let offset = 0;
      for (const pcm of pcmBuffers) {
        mergedPcm.set(pcm, offset);
        offset += pcm.length;
      }

      const audioBuffer = audioContext.createBuffer(1, totalLength, 16000);
      audioBuffer.getChannelData(0).set(mergedPcm);

      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.destination);
      source.onended = () => {
        isPlaying = false;
        console.log('音频播放结束');
        playNextInQueue(); // 播放结束后继续下一句
      };
      source.start();
      console.log('开始播放音频，总长度:', totalLength);
    };

    const stripOggContainer = (data) => {
      let arrayBuffer;
      if (data instanceof ArrayBuffer) {
        arrayBuffer = data;
      } else if (data.buffer instanceof ArrayBuffer) {
        arrayBuffer = data.buffer;
      } else {
        console.error('输入数据类型不支持:', data);
        return [data];
      }

      const dataView = new DataView(arrayBuffer);
      const frames = [];
      let offset = 0;

      while (offset < arrayBuffer.byteLength) {
        if (dataView.getUint32(offset) === 0x4F676753) { // 'OggS'
          const segmentTableLength = dataView.getUint8(offset + 26);
          const segmentTableOffset = offset + 27;
          let segmentOffset = segmentTableOffset + segmentTableLength;

          for (let i = 0; i < segmentTableLength; i++) {
            const segmentLength = dataView.getUint8(segmentTableOffset + i);
            const segmentData = arrayBuffer.slice(segmentOffset, segmentOffset + segmentLength);
            segmentOffset += segmentLength;

            const header = new TextDecoder().decode(segmentData.slice(0, 8));
            if (header === 'OpusHead' || header === 'OpusTags') {
              console.log(`跳过 ${header}，大小: ${segmentLength} 字节`);
            } else if (segmentLength >= 50 && segmentLength <= 300) {
              frames.push(segmentData);
            }
          }
          offset = segmentOffset;
        } else {
          const remainingLength = arrayBuffer.byteLength - offset;
          if (remainingLength >= 50 && remainingLength <= 300) {
            frames.push(arrayBuffer.slice(offset));
          }
          break;
        }
      }

      if (frames.length === 0) {
        console.warn('未找到有效裸 Opus 帧，返回原始数据');
        return [arrayBuffer];
      }
      console.log('剥离后找到', frames.length, '个裸 Opus 帧');
      return frames;
    };

    const initRecorder = async () => {
      console.log('开始初始化录音');
      try {
        if (stream) {
          stream.getTracks().forEach(track => track.stop());
        }
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log('获取麦克风权限成功，stream:', stream);

        if (!audioContext || audioContext.state === 'closed') {
          audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
        }
        sourceNode = audioContext.createMediaStreamSource(stream);

        recorder = new Recorder({
          encoderPath: '/encoderWorker.min.js',
          sampleRate: 16000,
          numberOfChannels: 1,
          frameSize: 960,
          encoderApplication: 2048,
          encoderFrameSize: 60,
          encoderBitRate: 24000,
          monitorGain: 0,
          sourceNode: sourceNode,
          ogg: false,
          streamPages: false,
          maxFramesPerPage: 1,
        });

        recorder.ondataavailable = (data) => {
          console.log('录音数据可用:', data.byteLength, '类型:', data.constructor.name);
          const frames = stripOggContainer(data);
          frames.forEach((frame, index) => {
            const frameView = new DataView(frame);
            const frameHead = Array.from(new Uint8Array(frame.slice(0, 8)))
                .map(b => b.toString(16).padStart(2, '0'))
                .join(' ');
            console.log(`帧 ${index} 大小: ${frame.byteLength} 字节，前8字节: ${frameHead}`);

            if (frame.byteLength < 50 || frame.byteLength > 300) {
              console.warn(`帧 ${index} 大小异常: ${frame.byteLength} 字节，预期 50-300 字节`);
              return;
            }

            if (ws && ws.readyState === WebSocket.OPEN) {
              ws.send(frame);
              console.log('发送裸 Opus 帧:', frame.byteLength);
            } else {
              console.warn('WebSocket 未连接，跳过发送');
            }
          });
        };

        recorder.onstart = () => {
          console.log('录音已启动');
        };

        recorder.onstop = () => {
          console.log('录音停止');
          stream.getTracks().forEach(track => track.stop());
          stream = null;
          sourceNode = null;
          scrollToBottom();
        };

        console.log('Recorder 初始化成功');
      } catch (err) {
        console.error('初始化录音失败:', err);
        alert('无法访问麦克风或录音初始化失败，请检查权限');
      }
    };

    const toggleRecording = async () => {
      console.log('点击 toggleRecording，当前状态:', isRecording.value, 'WebSocket 状态:', wsStatus.value);
      if (!recorder) {
        await initRecorder();
        if (!recorder) {
          console.error('recorder 初始化失败');
          return;
        }
      }
      if (isRecording.value) {
        console.log('停止录音');
        recorder.stop();
        isRecording.value = false;
      } else {
        try {
          console.log('开始录音');
          await initRecorder();
          await recorder.start();
          console.log('录音开始后，状态:', recorder.state);
          isRecording.value = true;
        } catch (err) {
          console.error('录音启动失败:', err);
        }
      }
    };

    onMounted(() => {
      console.log('组件挂载，初始化 WebSocket');
      connectWebSocket();
    });

    onUnmounted(() => {
      if (ws) ws.close();
      if (stream) stream.getTracks().forEach(track => track.stop());
      if (recorder) recorder.stop();
      if (audioContext) audioContext.close();
      if (audioDecoder) audioDecoder.destroy();
    });

    return { messages, chatContainer, wsStatus, isRecording, toggleRecording };
  }
};
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.title {
  text-align: center;
  font-size: 24px;
  margin-bottom: 20px;
}

.chat-container {
  height: 60vh;
  overflow-y: auto;
  border: 1px solid #ccc;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 5px;
}

.message {
  margin: 10px 0;
  padding: 8px 12px;
  border-radius: 5px;
  max-width: 70%;
}

.user {
  background: #007bff;
  color: white;
  margin-left: auto;
}

.assistant {
  background: #e9ecef;
  color: black;
}

.controls {
  text-align: center;
  margin-top: 20px;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

button.recording {
  background: #dc3545;
}
</style>