/**
 * Database 类 - 高层数据库 API
 * 封装用户、Agent、任务等操作的便捷方法
 */

const { getDatabaseManager } = require('./database-manager');

class Database {
  constructor(dbPath = null) {
    this.dbManager = getDatabaseManager(dbPath);
    this.dbManager.init();
  }

  /**
   * Agent 操作
   */
  async createAgent(agentData) {
    const {
      name,
      type = 'coder',
      status = 'idle',
      current_task_id = null,
      address = null,
      max_concurrent_tasks = 1,
      skills = '[]'
    } = agentData;
    const stmt = this.dbManager.db.prepare(`
            INSERT INTO agents (name, type, status, current_task_id, address, max_concurrent_tasks, skills, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        `);
    const result = stmt.run(
      name,
      type,
      status,
      current_task_id,
      address,
      max_concurrent_tasks,
      skills
    );

    return this.getAgent(result.lastInsertRowid);
  }

  async getAgents() {
    return this.dbManager.db.prepare('SELECT * FROM agents ORDER BY created_at DESC').all();
  }

  async getAgent(id) {
    return this.dbManager.db.prepare('SELECT * FROM agents WHERE id = ?').get(id);
  }

  async updateAgentStatus(id, status) {
    const stmt = this.dbManager.db.prepare(`
            UPDATE agents SET status = ?, updated_at = datetime('now') WHERE id = ?
        `);
    return stmt.run(status, id);
  }

  async updateAgentHeartbeat(id, lastHeartbeat = null) {
    const heartbeat = lastHeartbeat || new Date().toISOString();
    const stmt = this.dbManager.db.prepare(`
            UPDATE agents SET last_heartbeat = ?, updated_at = datetime('now') WHERE id = ?
        `);
    return stmt.run(heartbeat, id);
  }

  async updateAgentCurrentTask(id, currentTaskId) {
    const stmt = this.dbManager.db.prepare(`
            UPDATE agents SET current_task_id = ?, updated_at = datetime('now') WHERE id = ?
        `);
    return stmt.run(currentTaskId, id);
  }

  async getIdleAgents() {
    return this.dbManager.db.prepare("SELECT * FROM agents WHERE status = 'idle'").all();
  }

  async deleteAgent(id) {
    return this.dbManager.db.prepare('DELETE FROM agents WHERE id = ?').run(id);
  }

  /**
   * 任务操作
   */
  async createTask(taskData) {
    const {
      title,
      description = '',
      status = 'pending',
      priority = 2,
      assigned_agent_id = null,
      project_id = null
    } = taskData;
    const stmt = this.dbManager.db.prepare(`
            INSERT INTO tasks (title, description, status, priority, assigned_agent_id, project_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        `);
    const result = stmt.run(title, description, status, priority, assigned_agent_id, project_id);

    return this.getTask(result.lastInsertRowid);
  }

  async getTasks() {
    return this.dbManager.db.prepare('SELECT * FROM tasks ORDER BY created_at DESC').all();
  }

  async getTask(id) {
    return this.dbManager.db.prepare('SELECT * FROM tasks WHERE id = ?').get(id);
  }

  async updateTaskStatus(id, status) {
    const stmt = this.dbManager.db.prepare(`
            UPDATE tasks SET status = ?, updated_at = datetime('now') WHERE id = ?
        `);
    return stmt.run(status, id);
  }

  async assignTaskToAgent(taskId, agentId) {
    const stmt = this.dbManager.db.prepare(`
            UPDATE tasks SET assigned_agent_id = ?, status = 'in_progress', updated_at = datetime('now') WHERE id = ?
        `);
    return stmt.run(agentId, taskId);
  }

  async assignTask(taskId, agentId) {
    return this.assignTaskToAgent(taskId, agentId);
  }

  async deleteTask(id) {
    return this.dbManager.db.prepare('DELETE FROM tasks WHERE id = ?').run(id);
  }

  async getPendingTasks() {
    return this.dbManager.db
      .prepare("SELECT * FROM tasks WHERE status = 'pending' AND assigned_agent_id IS NULL")
      .all();
  }

  async getTasksByAgent(agentId) {
    return this.dbManager.db
      .prepare('SELECT * FROM tasks WHERE assigned_agent_id = ?')
      .all(agentId);
  }

  async getTaskStats() {
    const stats = this.dbManager.db
      .prepare(
        `
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM tasks
        `
      )
      .get();
    return stats;
  }

  /**
   * 用户操作
   */
  async createUser(userData) {
    const { username, email, password, role = 'user', status = 'active' } = userData;
    const stmt = this.dbManager.db.prepare(`
            INSERT INTO users (username, email, password, role, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        `);
    const result = stmt.run(username, email, password, role, status);

    return this.getUser(result.lastInsertRowid);
  }

  async getUsers() {
    return this.dbManager.db.prepare('SELECT * FROM users ORDER BY created_at DESC').all();
  }

  async getUser(id) {
    return this.dbManager.db.prepare('SELECT * FROM users WHERE id = ?').get(id);
  }

  async getUserByUsername(username) {
    return this.dbManager.db.prepare('SELECT * FROM users WHERE username = ?').get(username);
  }

  async getUserByEmail(email) {
    return this.dbManager.db.prepare('SELECT * FROM users WHERE email = ?').get(email);
  }

  async updateUser(id, updates) {
    const allowedFields = ['username', 'email', 'password', 'role', 'status'];
    const fields = Object.keys(updates).filter((f) => allowedFields.includes(f));

    if (fields.length === 0) {
      return { changes: 0 };
    }

    const setClause = fields.map((f) => `${f} = ?`).join(', ');
    const values = [...fields.map((f) => updates[f]), id];

    const stmt = this.dbManager.db.prepare(`
            UPDATE users SET ${setClause}, updated_at = datetime('now') WHERE id = ?
        `);

    return stmt.run(...values);
  }

  async updateUserPassword(id, newPassword) {
    const stmt = this.dbManager.db.prepare(`
            UPDATE users SET password = ?, updated_at = datetime('now') WHERE id = ?
        `);
    return stmt.run(newPassword, id);
  }

  async updateUserStatus(id, status) {
    const stmt = this.dbManager.db.prepare(`
            UPDATE users SET status = ?, updated_at = datetime('now') WHERE id = ?
        `);
    return stmt.run(status, id);
  }

  async deleteUser(id) {
    return this.dbManager.db.prepare('DELETE FROM users WHERE id = ?').run(id);
  }

  /**
   * 项目操作
   */
  async createProject(projectData) {
    const { name, description = '', status = 'active' } = projectData;
    const stmt = this.dbManager.db.prepare(`
            INSERT INTO projects (name, description, status, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
        `);
    const result = stmt.run(name, description, status);

    return this.getProject(result.lastInsertRowid);
  }

  async getProjects() {
    return this.dbManager.db.prepare('SELECT * FROM projects ORDER BY created_at DESC').all();
  }

  async getProject(id) {
    return this.dbManager.db.prepare('SELECT * FROM projects WHERE id = ?').get(id);
  }

  async deleteProject(id) {
    return this.dbManager.db.prepare('DELETE FROM projects WHERE id = ?').run(id);
  }

  /**
   * 配置操作
   */
  async setConfig(key, value, description = '') {
    const stmt = this.dbManager.db.prepare(`
            INSERT OR REPLACE INTO configs (key, value, description, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
        `);
    return stmt.run(key, value, description);
  }

  async getConfig(key) {
    return this.dbManager.db.prepare('SELECT * FROM configs WHERE key = ?').get(key);
  }

  async getAllConfigs() {
    return this.dbManager.db.prepare('SELECT * FROM configs ORDER BY key').all();
  }

  /**
   * 关闭数据库连接
   */
  close() {
    this.dbManager.close();
  }
}

module.exports = { Database };
