import { generateService } from '@umijs/openapi'
generateService({
  requestLibPath: "import request from '@/request'",// 引入自定义的 Axios 实例
  schemaPath: 'http://localhost:8123/api/v2/api-docs',// API 文档路径
  serversPath: './src',// 生成的代码路径
})

