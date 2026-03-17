#!/usr/bin/env node
/**
 * Xiangqin CLI
 */

const { Xiangqin } = require('./index');

const app = new Xiangqin();

function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const userId = args[1] || 'user_default';

  try {
    switch (command) {
      case 'profile':
      case '资料': {
        const action = args[2];
        if (action === 'create' || action === '创建') {
          const info = JSON.parse(args[3] || '{}');
          const result = app.createProfile(userId, info);
          console.log(JSON.stringify(result, null, 2));
        } else {
          const profile = app.getProfile(userId);
          if (profile) {
            console.log('=== 我的资料 ===');
            console.log(`昵称: ${profile.basicInfo.nickname}`);
            console.log(`性别: ${profile.basicInfo.gender}`);
            console.log(`年龄: ${profile.basicInfo.age}`);
            console.log(`身高: ${profile.basicInfo.height}cm`);
            console.log(`学历: ${profile.basicInfo.education}`);
            console.log(`职业: ${profile.basicInfo.occupation}`);
            console.log(`收入: ${profile.basicInfo.income}`);
            console.log(`所在地: ${profile.basicInfo.location}`);
            console.log(`\n资料完整度: ${app.calculateCompleteness(profile).percentage}%`);
          } else {
            console.log('尚未创建资料');
          }
        }
        break;
      }

      case 'match':
      case '匹配': {
        const limit = parseInt(args[2]) || 5;
        const result = app.findMatches(userId, { limit });
        if (result.success) {
          console.log(`=== 推荐匹配 (${result.total}人) ===\n`);
          result.matches.forEach((m, i) => {
            console.log(`${i + 1}. ${m.profile.basicInfo.nickname}`);
            console.log(`   ${m.profile.basicInfo.age}岁 | ${m.profile.basicInfo.height}cm | ${m.profile.basicInfo.education}`);
            console.log(`   ${m.profile.basicInfo.occupation} | ${m.profile.basicInfo.location}`);
            console.log(`   匹配度: ${m.matchScore.percentage}% - ${m.matchScore.level}`);
            if (m.matchScore.details.hobbies.common?.length > 0) {
              console.log(`   共同爱好: ${m.matchScore.details.hobbies.common.join('、')}`);
            }
            console.log();
          });
        } else {
          console.log(result.error);
        }
        break;
      }

      case 'opener':
      case '开场白': {
        const targetId = args[2];
        if (!targetId) {
          console.log('用法: xiangqin opener <对方ID>');
          process.exit(1);
        }
        const myProfile = app.getProfile(userId);
        const theirProfile = app.getProfile(targetId);
        if (!myProfile || !theirProfile) {
          console.log('资料不完整');
          process.exit(1);
        }
        const result = app.generateOpener(myProfile, theirProfile, {
          commonHobbies: ['旅游', '电影']
        });
        console.log('=== 推荐开场白 ===\n');
        result.recommendations.forEach((r, i) => {
          console.log(`${i + 1}. [${r.type}] ${r.content}`);
        });
        console.log('\n💡 提示:');
        result.tips.forEach(t => console.log(`   ${t}`));
        break;
      }

      case 'topics':
      case '话题': {
        const stage = args[2] || 'initial';
        const result = app.suggestTopics(null, null, stage);
        console.log(`=== ${stage === 'initial' ? '初次' : stage === 'middle' ? '深入' : '进阶'}话题 ===\n`);
        result.topics.forEach(t => {
          console.log(`📌 ${t.topic}`);
          t.questions.forEach(q => console.log(`   • ${q}`));
          console.log();
        });
        break;
      }

      case 'date':
      case '约会': {
        const location = args[2] || '北京';
        const result = app.suggestDateIdeas(location);
        console.log(`=== ${location}约会建议 ===\n`);
        for (const [stage, ideas] of Object.entries(result.suggestions)) {
          console.log(`\n【${stage === 'first' ? '初次' : stage === 'second' ? '第二次' : '进阶'}约会】`);
          ideas.forEach(idea => {
            console.log(`  ${idea.name}`);
            console.log(`    优点: ${idea.pros.join('、')}`);
            console.log(`    缺点: ${idea.cons.join('、')}`);
          });
        }
        break;
      }

      case 'contact':
      case '记录': {
        const targetId = args[2];
        const content = args.slice(3).join(' ');
        if (!targetId || !content) {
          console.log('用法: xiangqin contact <对方ID> <记录内容>');
          process.exit(1);
        }
        const result = app.recordContact(userId, targetId, {
          type: 'message',
          content
        });
        console.log('接触记录已保存');
        break;
      }

      case 'history':
      case '历史': {
        const targetId = args[2];
        if (!targetId) {
          console.log('用法: xiangqin history <对方ID>');
          process.exit(1);
        }
        const history = app.getContactHistory(userId, targetId);
        if (history) {
          console.log(`=== 接触历史 ===`);
          console.log(`状态: ${history.status}`);
          console.log(`开始时间: ${history.startedAt}`);
          console.log(`接触次数: ${history.contacts.length}`);
          history.contacts.forEach((c, i) => {
            console.log(`\n${i + 1}. [${c.type}] ${c.timestamp}`);
            console.log(`   ${c.content}`);
          });
        } else {
          console.log('暂无接触记录');
        }
        break;
      }

      case 'safety':
      case '安全': {
        const tips = app.getSafetyTips();
        console.log('=== 安全提醒 ===\n');
        console.log('【见面前】');
        tips.before.forEach(t => console.log(`  ${t}`));
        console.log('\n【见面时】');
        tips.during.forEach(t => console.log(`  ${t}`));
        console.log('\n【危险信号】');
        tips.redFlags.forEach(t => console.log(`  ${t}`));
        console.log('\n【常见骗局】');
        tips.scams.forEach(t => console.log(`  ${t}`));
        break;
      }

      default:
        console.log(`
相亲助手 - Xiangqin

用法:
  xiangqin profile <用户ID> [create <资料JSON>]    查看/创建资料
  xiangqin match <用户ID> [数量]                    寻找匹配
  xiangqin opener <用户ID> <对方ID>                生成开场白
  xiangqin topics [initial/middle/advanced]        推荐话题
  xiangqin date [城市]                             约会建议
  xiangqin contact <用户ID> <对方ID> <内容>        记录接触
  xiangqin history <用户ID> <对方ID>               查看历史
  xiangqin safety                                  安全提醒

示例:
  xiangqin profile user1 create '{"nickname":"小明","gender":"男","birthYear":1995,"height":175,"location":"北京","education":"本科","occupation":"程序员","hobbies":["旅游","电影"]}'
  xiangqin match user1 10
  xiangqin opener user1 user2
        `);
    }
  } catch (error) {
    console.error('错误:', error.message);
    process.exit(1);
  }
}

main();
