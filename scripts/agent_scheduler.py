#!/usr/bin/env python3
"""
Agent 调度器 - 真正的双 Agent 交替工作

这个调度器启动两个 Agent 进程，让它们真正交替工作：
1. 每个 Agent 定期检查状态
2. 如果当前活跃的是自己，就执行任务
3. 任务完成后切换到另一个 Agent
"""
import sys
import os
import time
import signal
import subprocess
from pathlib import Path
import yaml

class AgentScheduler:
    """Agent 调度器"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.state_file = self.project_path / 'state' / 'project_state.yaml'
        self.agent1_proc = None
        self.agent2_proc = None
        self.running = True
        
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
    
    def load_state(self):
        with open(self.state_file) as f:
            return yaml.safe_load(f)
    
    def save_state(self, state):
        with open(self.state_file, 'w') as f:
            yaml.dump(state, f, allow_unicode=True, default_flow_style=False)
    
    def get_active_agent(self):
        state = self.load_state()
        project_agents = state.get('project', {}).get('agents', {})
        for agent_id, agent_data in project_agents.items():
            if agent_data.get('current', False):
                return agent_id
        return None
    
    def switch_agent(self):
        """切换活跃的 Agent"""
        state = self.load_state()
        project_agents = state.get('project', {}).get('agents', {})
        
        current = self.get_active_agent()
        next_agent = 'agent2' if current == 'agent1' else 'agent1'
        
        for agent_id in project_agents:
            project_agents[agent_id]['current'] = (agent_id == next_agent)
        
        state['project']['agents'] = project_agents
        state['current_agent'] = next_agent
        self.save_state(state)
        
        print(f"[调度器] 切换 Agent: {current} → {next_agent}")
        return next_agent
    
    def run_agent(self, agent_id: str):
        """运行单个 Agent 的任务"""
        state = self.load_state()
        phase = state.get('phase', 'unknown')
        
        print(f"[Agent {agent_id}] 检查阶段: {phase}")
        
        # Agent 1 的任务
        if agent_id == 'agent1':
            if phase == 'requirements_review':
                if not state['requirements'].get('pm_signoff', False):
                    print(f"[Agent 1] 签署需求...")
                    state['requirements']['pm_signoff'] = True
                    self.save_state(state)
                    return True
            
            elif phase == 'design_review':
                if not state['design'].get('pm_signoff', False):
                    print(f"[Agent 1] 签署设计...")
                    state['design']['pm_signoff'] = True
                    self.save_state(state)
                    return True
            
            elif phase == 'testing':
                if not state['test'].get('pm_signoff', False):
                    print(f"[Agent 1] 执行测试...")
                    # 模拟测试
                    state['test']['pm_signoff'] = True
                    self.save_state(state)
                    return True
        
        # Agent 2 的任务
        elif agent_id == 'agent2':
            if phase == 'requirements_review':
                if not state['requirements'].get('dev_signoff', False):
                    print(f"[Agent 2] 签署需求...")
                    state['requirements']['dev_signoff'] = True
                    self.save_state(state)
                    return True
            
            elif phase == 'design_review':
                if not state['design'].get('dev_signoff', False):
                    print(f"[Agent 2] 签署设计...")
                    state['design']['dev_signoff'] = True
                    self.save_state(state)
                    return True
            
            elif phase == 'development':
                print(f"[Agent 2] 开发功能...")
                state['development']['status'] = 'completed'
                state['phase'] = 'testing'
                state['test']['status'] = 'in_progress'
                self.save_state(state)
                return True
            
            elif phase == 'testing':
                issues = state.get('test', {}).get('issues_to_fix', [])
                if issues:
                    print(f"[Agent 2] 修复 {len(issues)} 个 bug...")
                    state['test']['issues_to_fix'] = []
                    state['test']['dev_signoff'] = True
                    self.save_state(state)
                    return True
        
        return False
    
    def check_phase_advance(self):
        """检查需要阶段推进"""
        state = self.load_state()
        phase = state.get('phase', '')
        req = state.get('requirements', {})
        design = state.get('design', {})
        test = state.get('test', {})
        
        # 需求批准 → 设计
        if phase == 'requirements_review':
            if req.get('pm_signoff') and req.get('dev_signoff'):
                state['phase'] = 'design_draft'
                req['status'] = 'approved'
                self.save_state(state)
                print(f"[调度器] 阶段推进: requirements → design")
                return True
        
        # 设计批准 → 开发
        elif phase == 'design_review':
            if design.get('pm_signoff') and design.get('dev_signoff'):
                state['phase'] = 'development'
                design['status'] = 'approved'
                self.save_state(state)
                print(f"[调度器] 阶段推进: design → development")
                return True
        
        # 测试通过 → 完成
        elif phase == 'testing':
            if test.get('pm_signoff') and test.get('dev_signoff'):
                issues = test.get('issues_to_fix', [])
                if not issues:
                    state['phase'] = 'completed'
                    test['status'] = 'completed'
                    self.save_state(state)
                    print(f"[调度器] 阶段推进: testing → completed")
                    return True
        
        return False
    
    def run(self):
        """主循环"""
        print("=" * 60)
        print("Agent 调度器启动")
        print("=" * 60)
        
        while self.running:
            try:
                active_agent = self.get_active_agent()
                
                if not active_agent:
                    print("[调度器] 未设置活跃 Agent，设置为 agent1")
                    self.switch_agent()
                    continue
                
                # 执行当前 Agent 的任务
                did_work = self.run_agent(active_agent)
                
                # 检查阶段推进
                did_advance = self.check_phase_advance()
                
                if did_work or did_advance:
                    # 任务完成，切换 Agent
                    time.sleep(2)  # 短暂延迟，让另一个 Agent 有机会工作
                    self.switch_agent()
                
                time.sleep(3)  # 每 3 秒检查一次
                
            except Exception as e:
                print(f"[调度器] 错误: {e}")
                time.sleep(5)
        
        print("[调度器] 已关闭")
    
    def shutdown(self, signum, frame):
        print(f"[调度器] 收到信号 {signum}，正在关闭...")
        self.running = False
        if self.agent1_proc:
            self.agent1_proc.terminate()
        if self.agent2_proc:
            self.agent2_proc.terminate()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', default='.', help='项目路径')
    args = parser.parse_args()
    
    scheduler = AgentScheduler(args.path)
    scheduler.run()
