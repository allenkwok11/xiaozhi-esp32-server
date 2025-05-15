package xiaozhi.modules.security.service.impl;

import java.io.IOException;
import java.util.Random;
import java.util.concurrent.TimeUnit;

import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;
import com.wf.captcha.SpecCaptcha;
import com.wf.captcha.base.Captcha;

import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletResponse;
import xiaozhi.common.redis.RedisKeys;
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.modules.security.service.CaptchaService;
import xiaozhi.modules.sms.service.SmsService;

/**
 * 验证码
 */
@Service
public class CaptchaServiceImpl implements CaptchaService {
    @Resource
    private RedisUtils redisUtils;
    @Resource
    private SmsService smsService;
    @Value("${renren.redis.open}")
    private boolean open;
    /**
     * Local Cache 5分钟过期
     */
    Cache<String, String> localCache = CacheBuilder.newBuilder().maximumSize(1000)
            .expireAfterAccess(5, TimeUnit.MINUTES).build();

    @Override
    public void create(HttpServletResponse response, String uuid) throws IOException {
        response.setContentType("image/gif");
        response.setHeader("Pragma", "No-cache");
        response.setHeader("Cache-Control", "no-cache");
        response.setDateHeader("Expires", 0);

        // 生成验证码
        SpecCaptcha captcha = new SpecCaptcha(150, 40);
        captcha.setLen(5);
        captcha.setCharType(Captcha.TYPE_DEFAULT);
        captcha.out(response.getOutputStream());

        // 保存到缓存
        setCache(uuid, captcha.text());
    }

    @Override
    public boolean validate(String uuid, String code) {
        if (StringUtils.isBlank(code)) {
            return false;
        }
        // 获取验证码
        String captcha = getCache(uuid);

        // 效验成功
        if (code.equalsIgnoreCase(captcha)) {
            return true;
        }

        return false;
    }

    @Override
    public void sendSMSValidateCode(String phone) {
        String key = RedisKeys.getSMSValidateCodeKey(phone);
        String validateCodes = generateValidateCode(6);
        setCache(key,validateCodes);
        //发送验证码短信
        smsService.sendVerificationCodeSms(phone,validateCodes);
    }

    @Override
    public boolean validateSMSValidateCode(String phone,String code) {
        String key = RedisKeys.getSMSValidateCodeKey(phone);
        return validate(key, code);
    }
    /**
     * 生成指定数量的随机数验证码
     * @param length 数量
     * @return 随机码
     */
    private  String generateValidateCode(Integer length) {
        String chars = "0123456789"; // 字符范围可以自定义：数字
        Random random = new Random();
        StringBuilder code = new StringBuilder();
        for (int i = 0; i < length; i++) {
            code.append(chars.charAt(random.nextInt(chars.length())));
        }
        return code.toString();
    }

    private void setCache(String key, String value) {
        if (open) {
            key = RedisKeys.getCaptchaKey(key);
            redisUtils.set(key, value, 300);
        } else {
            localCache.put(key, value);
        }
    }

    private String getCache(String key) {
        if (open) {
            key = RedisKeys.getCaptchaKey(key);
            String captcha = (String) redisUtils.get(key);
            // 删除验证码
            if (captcha != null) {
                redisUtils.delete(key);
            }

            return captcha;
        }

        String captcha = localCache.getIfPresent(key);
        // 删除验证码
        if (captcha != null) {
            localCache.invalidate(key);
        }
        return captcha;
    }
}