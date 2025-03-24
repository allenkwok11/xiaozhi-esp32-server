package xiaozhi.modules.model.mapper;

import org.apache.ibatis.annotations.Mapper;
import xiaozhi.modules.model.domain.TtsVoice;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;

/**
* @author chenerlei
* @description 针对表【ai_tts_voice(TTS 音色表)】的数据库操作Mapper
* @createDate 2025-03-22 15:31:57
* @Entity xiaozhi.modules.model.domain.TtsVoice
*/
@Mapper
public interface TtsVoiceMapper extends BaseMapper<TtsVoice> {

}




