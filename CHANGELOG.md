## v1.0.2

### 新增
- ARM64 架构支持（linux-arm64, macos-arm64）
- 域名自动探测（18 个已知域名轮询）

### 变更
- Cookie 直接写入 config.json，移除独立 cookie 文件
- 简化文件结构，删除冗余脚本
- 域名探测改为轮询方式

### 构建
- 5 个架构同时编译：windows-amd64, linux-amd64, linux-arm64, macos-amd64, macos-arm64
