# 使用Node.js官方镜像作为基础镜像
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 安装pnpm
RUN npm install -g pnpm

# 复制package.json和pnpm-lock.yaml
COPY package.json pnpm-lock.yaml ./

# 安装依赖
RUN pnpm install --frozen-lockfile

# 复制项目文件
COPY . .

# 构建项目
RUN pnpm build:h5

# 创建输出目录
RUN mkdir -p /app/dist

# 复制构建产物
RUN cp -r /app/dist/build/h5/* /app/dist/ || cp -r /app/dist/* /app/dist/

# 使用轻量级镜像作为最终阶段
FROM alpine:latest

# 创建目录
RUN mkdir -p /usr/share/nginx/html

# 复制构建产物
COPY --from=0 /app/dist /usr/share/nginx/html

# 设置权限
RUN chmod -R 755 /usr/share/nginx/html

# 创建一个简单的健康检查文件
RUN echo "Frontend build completed" > /usr/share/nginx/html/health.txt 