package xiaozhi.common.config;

import org.springdoc.core.models.GroupedOpenApi;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;

/**
 * Swagger配置
 * Copyright (c) 人人开源 All rights reserved.
 * Website: https://www.renren.io
 */
@Configuration
public class SwaggerConfig {

    @Bean
    public GroupedOpenApi userApi() {
        String[] paths = { "/**" };
        return GroupedOpenApi.builder().group("xiaozhi")
                .pathsToMatch(paths).build();
    }

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI().info(new Info()
                .title("xiaozhi-esp32-manager-api")
                .description("xiaozhi-esp32-manager-api文档")
                .version("3.0")
                .termsOfService("https://127.0.0.1"));
    }
}