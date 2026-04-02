"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const form_data_1 = __importDefault(require("form-data"));
const node_fetch_1 = __importDefault(require("node-fetch"));
// 日志文件配置
const LOG_DIR = path.join(process.env.TEMP || process.env.TMP || '/tmp', 'openclaw-logs', 'ai-redaction');
const LOG_FILE = path.join(LOG_DIR, 'debug.log');
// 确保日志目录存在
function ensureLogDir() {
    if (!fs.existsSync(LOG_DIR)) {
        fs.mkdirSync(LOG_DIR, { recursive: true });
    }
}
// 写入日志到文件
function writeToFile(level, message) {
    try {
        ensureLogDir();
        const timestamp = new Date().toISOString();
        const logLine = `[${timestamp}] [${level}] ${message}\n`;
        fs.appendFileSync(LOG_FILE, logLine);
    }
    catch (err) {
        // 静默处理，避免日志写入失败影响主流程
    }
}
/**
 * 日志实现
 */
const log = {
    info: (msg) => {
        console.log(`[INFO] ${msg}`);
        writeToFile('INFO', msg);
    },
    error: (msg) => {
        console.error(`[ERROR] ${msg}`);
        writeToFile('ERROR', msg);
    },
    debug: (msg) => {
        console.debug(`[DEBUG] ${msg}`);
        writeToFile('DEBUG', msg);
    },
    warn: (msg) => {
        console.warn(`[WARN] ${msg}`);
        writeToFile('WARN', msg);
    }
};
/**
 * AI 文件脱敏技能
 */
class AIRedactionSkill {
    constructor() {
        this.API_VERSION = 'v1';
        this.API_BASE_URL = process.env.AI_REDACTION_API_URL || 'https://openapi4aitest.bestcoffer.com.cn/';
        this.WEBSITE_URL = process.env.AI_REDACTION_WEBSITE_URL || 'https://airedact_file_test.bestcoffer.com.cn/';
    }
    /**
     * 验证文件
     */
    validateFile(file) {
        if (!file) {
            throw new Error('未接收到文件，请重新上传');
        }
        // const supportedTypes = ['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx'];
        // const fileExt = path.extname(file.name).toLowerCase().slice(1);
        // if (!supportedTypes.includes(fileExt)) {
        //   throw new Error(`不支持的文件格式：${fileExt}。支持的格式：${supportedTypes.join(', ')}`);
        // }
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            throw new Error(`文件大小超过限制（10MB）：${(file.size / 1024 / 1024).toFixed(2)}MB`);
        }
    }
    /**
     * 验证脱敏指令
     */
    validateInstruction(instruction) {
        if (!instruction || instruction.trim() === '') {
            throw new Error('请提供脱敏指令');
        }
    }
    /**
     * 调用脱敏 API 上传文件并创建任务
     */
    async uploadAndCreateTask(file, instruction, apiKey) {
        const endpoint = `${this.API_BASE_URL}redaction/upload`;
        log.debug(`上传文件到：${endpoint}`);
        log.debug(`文件信息：${JSON.stringify({ name: file.name, size: file.size, type: file.type })}`);
        log.debug(`脱敏指令：${instruction}`);
        log.debug(`API key：${apiKey}`);
        const form = new form_data_1.default();
        form.append('file', fs.createReadStream(file.path), {
            filename: file.name,
            contentType: file.type || 'application/octet-stream'
        });
        form.append('instruction', instruction);
        const response = await (0, node_fetch_1.default)(endpoint, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                ...form.getHeaders()
            },
            body: form
        });
        if (!response.ok) {
            const errorText = await response.text();
            log.error(`API 请求失败：${response.status} - ${errorText}`);
            throw new Error(`API 请求失败：${response.status}`);
        }
        const result = await response.json();
        if (result.code !== 1) {
            throw new Error(result.message);
        }
        const data = result.data;
        // 拼接 url
        const taskUrl = `${this.WEBSITE_URL}?fileId=${data.fileId}&apiKey=${apiKey}`;
        return {
            taskId: data.fileId,
            taskUrl: taskUrl
        };
    }
    /**
     * 执行文件脱敏
     */
    async execute(context) {
        try {
            log.debug(`[日志文件] ${LOG_FILE}`);
            log.info('开始处理文件脱敏请求');
            const { file, instruction, apiKey } = context.parameters;
            // 验证参数
            this.validateFile(file);
            this.validateInstruction(instruction);
            if (!apiKey) {
                throw new Error('API key 未配置，请先设置 API key');
            }
            log.info(`收到文件：${file.name}, 大小：${(file.size / 1024).toFixed(2)}KB`);
            log.debug(`脱敏指令：${instruction}`);
            log.debug(`API key：${apiKey}`);
            // 调用 API 创建脱敏任务
            const result = await this.uploadAndCreateTask(file, instruction, apiKey);
            log.info(`任务创建成功，查询链接：${result.taskUrl}`);
            return {
                taskUrl: result.taskUrl
            };
        }
        catch (error) {
            log.error(`处理失败：${error}`);
            throw error;
        }
    }
}
// 导出技能实例
exports.default = new AIRedactionSkill();
