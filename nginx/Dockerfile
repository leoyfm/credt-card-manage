FROM nginx:alpine

# 复制自定义nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 创建静态文件目录
RUN mkdir -p /usr/share/nginx/html

# 复制前端构建产物（这将在docker-compose中通过卷挂载）
# COPY --from=frontend /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/nginx-health || exit 1

# 启动nginx
CMD ["nginx", "-g", "daemon off;"] 