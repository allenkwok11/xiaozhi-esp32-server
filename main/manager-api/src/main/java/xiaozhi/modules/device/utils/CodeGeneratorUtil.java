package xiaozhi.modules.device.utils;

import java.util.Random;

public class CodeGeneratorUtil {

    private static long lastTime = 0;
    private static int counter = 0;

    /**
     * 生成6位数字码，首位不为0，短期内不会重复。
     * @return 6位数字码
     */
    public static synchronized String generateCode() {
        long currentTime = System.currentTimeMillis();
        
        // 如果当前时间与上次相同，增加计数器以避免重复
        if (currentTime == lastTime) {
            counter++;
        } else {
            counter = 0; // 时间变化时重置计数器
        }
        lastTime = currentTime;

        // 使用当前时间和计数器生成随机种子
        long seed = currentTime + counter;
        Random random = new Random(seed);

        // 确保首位不为0
        int firstDigit = random.nextInt(9) + 1;
        int remainingDigits = random.nextInt(100000); // 剩余5位

        // 拼接生成的6位数字码
        return String.format("%d%05d", firstDigit, remainingDigits);
    }

    /**
     * 生成指定位数的数字码，首位不为0，短期内不会重复。
     * @param digits 生成的数字码位数
     * @return 指定位数的数字码
     */
    public static synchronized String generateCode(int digits) {
        if (digits < 2) {
            throw new IllegalArgumentException("数字码位数必须大于等于2");
        }

        long currentTime = System.currentTimeMillis();
        
        // 如果当前时间与上次相同，增加计数器以避免重复
        if (currentTime == lastTime) {
            counter++;
        } else {
            counter = 0; // 时间变化时重置计数器
        }
        lastTime = currentTime;

        // 使用当前时间和计数器生成随机种子
        long seed = currentTime + counter;
        Random random = new Random(seed);

        // 确保首位不为0
        int firstDigit = random.nextInt(9) + 1;
        int remainingDigits = random.nextInt((int) Math.pow(10, digits - 1)); // 剩余位数

        // 拼接生成的动态位数数字码
        return String.format("%d%0" + (digits - 1) + "d", firstDigit, remainingDigits);
    }
}