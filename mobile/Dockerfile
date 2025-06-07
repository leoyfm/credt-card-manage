# 使用Node.js官方镜像作为基础镜像
FROM node:18-alpine as builder

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

# 使用nginx作为生产环境
FROM nginx:alpine

# 复制构建产物到nginx目录
COPY --from=builder /app/dist/build/h5 /usr/share/nginx/html

# 复制nginx配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"] 