#!/usr/bin/env node
/**
 * Cognitive Brain v5.3.25 - 系统要求检查
 * 检查 OpenClaw、Node.js、PostgreSQL、Redis 版本兼容性
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const HOME = process.env.HOME || '/root';

console.log('\n🔍 Cognitive Brain v5.3.25 系统要求检查\n');
console.log('='.repeat(50));

// 版本要求
const REQUIREMENTS = {
  node: { min: '18.0.0', recommended: '20.0.0', name: 'Node.js' },
  openclaw: { min: '2026.1.0', recommended: '2026.3.0', name: 'OpenClaw' },
  postgresql: { min: '14.0.0', recommended: '16.0.0', name: 'PostgreSQL' },
  redis: { min: '6.0.0', recommended: '7.0.0', name: 'Redis' }
};

// 版本比较函数
function compareVersions(v1, v2) {
  const parts1 = v1.split('.').map(Number);
  const parts2 = v2.split('.').map(Number);
  
  for (let i = 0; i < Math.max(parts1.length, parts2.length); i++) {
    const p1 = parts1[i] || 0;
    const p2 = parts2[i] || 0;
    if (p1 > p2) return 1;
    if (p1 < p2) return -1;
  }
  return 0;
}

// 解析版本号
function parseVersion(output, patterns) {
  for (const pattern of patterns) {
    const match = output.match(pattern);
    if (match) return match[1];
  }
  return null;
}

let allRequiredOk = true;
let warnings = [];

// 1. 检查 Node.js
console.log('\n📦 Node.js');
try {
  const version = execSync('node -v', { encoding: 'utf8' }).trim();
  const versionNum = version.replace('v', '');
  
  if (compareVersions(versionNum, REQUIREMENTS.node.min) >= 0) {
    if (compareVersions(versionNum, REQUIREMENTS.node.recommended) >= 0) {
      console.log(`  ✅ ${version} (推荐版本)`);
    } else {
      console.log(`  ✅ ${version} (满足最低要求)`);
      warnings.push(`Node.js 建议升级到 v${REQUIREMENTS.node.recommended}+`);
    }
  } else {
    console.log(`  ❌ ${version} (需要 >= v${REQUIREMENTS.node.min})`);
    allRequiredOk = false;
  }
} catch (e) {
  console.log('  ❌ 未安装');
  allRequiredOk = false;
}

// 2. 检查 OpenClaw
console.log('\n🤖 OpenClaw');
try {
  const versionOutput = execSync('openclaw --version 2>/dev/null || openclaw -v 2>/dev/null', { 
    encoding: 'utf8',
    stdio: ['pipe', 'pipe', 'pipe']
  });
  
  const version = parseVersion(versionOutput, [/(\d{4}\.\d+\.\d+)/, /v?(\d+\.\d+\.\d+)/]);
  
  if (version) {
    if (compareVersions(version, REQUIREMENTS.openclaw.min) >= 0) {
      console.log(`  ✅ v${version}`);
      
      // 检查配置文件
      const configPath = path.join(HOME, '.openclaw', 'openclaw.json');
      if (fs.existsSync(configPath)) {
        console.log('  ✅ 配置文件存在');
      } else {
        console.log('  ⚠️  配置文件不存在，请先运行 openclaw wizard');
        warnings.push('请运行: openclaw wizard');
      }
    } else {
      console.log(`  ❌ v${version} (需要 >= v${REQUIREMENTS.openclaw.min})`);
      warnings.push(`请升级 OpenClaw: npm update -g openclaw`);
    }
  } else {
    console.log('  ⚠️  无法获取版本');
    warnings.push('请确保 OpenClaw 已正确安装');
  }
} catch (e) {
  console.log('  ❌ 未安装或不在 PATH 中');
  console.log('     安装: npm install -g openclaw');
  allRequiredOk = false;
}

// 3. 检查 PostgreSQL
console.log('\n🗄️  PostgreSQL');
try {
  const versionOutput = execSync('psql --version', { encoding: 'utf8' });
  const version = parseVersion(versionOutput, [/(\d+(?:\.\d+)?)/]);
  
  if (version) {
    const majorVersion = version.split('.')[0];
    
    if (parseInt(majorVersion) >= 14) {
      console.log(`  ✅ PostgreSQL ${version}`);
      
      // 检查服务状态
      try {
        execSync('pg_isready', { encoding: 'utf8', stdio: 'pipe' });
        console.log('  ✅ 服务运行中');
        
        // 检查 pgvector 扩展
        try {
          const extCheck = execSync(
            'psql -U postgres -t -c "SELECT 1 FROM pg_available_extensions WHERE name = \'vector\'"',
            { encoding: 'utf8', stdio: 'pipe' }
          );
          if (extCheck.includes('1')) {
            console.log('  ✅ pgvector 扩展可用');
          } else {
            console.log('  ⚠️  pgvector 扩展未安装');
            warnings.push(`安装 pgvector: sudo apt install postgresql-${majorVersion}-pgvector`);
          }
        } catch (e) {
          console.log('  ⚠️  无法检查 pgvector');
        }
      } catch (e) {
        console.log('  ❌ 服务未运行');
        console.log('     启动: sudo systemctl start postgresql');
        allRequiredOk = false;
      }
    } else {
      console.log(`  ❌ PostgreSQL ${version} (需要 >= 14)`);
      allRequiredOk = false;
    }
  }
} catch (e) {
  console.log('  ❌ 未安装');
  console.log('     安装: sudo apt install postgresql postgresql-contrib');
  allRequiredOk = false;
}

// 4. 检查 Redis
console.log('\n⚡ Redis');
try {
  const pong = execSync('redis-cli ping', { encoding: 'utf8', stdio: 'pipe' });
  
  if (pong.includes('PONG')) {
    console.log('  ✅ 服务运行中');
    
    // 获取版本
    try {
      const info = execSync('redis-cli INFO server', { encoding: 'utf8' });
      const version = parseVersion(info, [/redis_version:(\d+\.\d+\.\d+)/]);
      if (version) {
        if (compareVersions(version, REQUIREMENTS.redis.recommended) >= 0) {
          console.log(`  ✅ Redis ${version}`);
        } else {
          console.log(`  ✅ Redis ${version} (满足要求)`);
        }
      }
    } catch (e) {}
  }
} catch (e) {
  console.log('  ❌ 未运行或未安装');
  console.log('     安装: sudo apt install redis-server');
  console.log('     启动: sudo systemctl start redis-server');
  allRequiredOk = false;
}

// 5. 检查系统资源
console.log('\n💾 系统资源');
try {
  const memInfo = execSync('free -m | grep Mem', { encoding: 'utf8' });
  const totalMem = parseInt(memInfo.split(/\s+/)[1]);
  
  if (totalMem >= 2048) {
    console.log(`  ✅ 内存: ${Math.round(totalMem / 1024)} GB`);
  } else {
    console.log(`  ⚠️  内存: ${Math.round(totalMem / 1024)} GB (建议 >= 2 GB)`);
    warnings.push('系统内存较低，可能影响性能');
  }
  
  const diskInfo = execSync('df -m / | tail -1', { encoding: 'utf8' });
  const availDisk = parseInt(diskInfo.split(/\s+/)[3]);
  
  if (availDisk >= 1024) {
    console.log(`  ✅ 磁盘: ${Math.round(availDisk / 1024)} GB 可用`);
  } else {
    console.log(`  ⚠️  磁盘: ${Math.round(availDisk / 1024)} GB 可用 (建议 >= 1 GB)`);
    warnings.push('磁盘空间较低');
  }
} catch (e) {
  console.log('  ⚠️  无法检查系统资源');
}

// 总结
console.log('\n' + '='.repeat(50));

if (allRequiredOk && warnings.length === 0) {
  console.log('\n✅ 系统检查通过，可以安装!\n');
  console.log('运行安装:');
  console.log('  clawhub install cognitive-brain');
  console.log('  或');
  console.log('  npm install && npm run setup\n');
  process.exit(0);
} else if (allRequiredOk) {
  console.log('\n⚠️  系统满足要求，但有以下建议:\n');
  warnings.forEach(w => console.log(`  • ${w}`));
  console.log('\n可以继续安装，但建议先处理上述问题\n');
  process.exit(0);
} else {
  console.log('\n❌ 系统不满足最低要求，请先安装缺失的依赖\n');
  console.log('快速安装 (Ubuntu/Debian):');
  console.log('  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -');
  console.log('  sudo apt update');
  console.log('  sudo apt install -y nodejs postgresql postgresql-contrib redis-server');
  console.log('  sudo systemctl start postgresql redis-server');
  console.log('  npm install -g openclaw\n');
  process.exit(1);
}
