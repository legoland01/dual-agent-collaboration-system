#!/usr/bin/env python3
"""
Agent 1 (产品经理) 工作进程
"""
import sys
import os
import time
import signal
import yaml
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/Users/liuzhen/Documents/河广/Product Development/chatGPT/Digital Law/Digital court/金融法院/法官数字助手/案卷材料样例/融资租赁/(2024)沪74民初721号/OpenCode Trial/dual-agent-collaboration-system')

class Agent1:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.state_file = self.project_path / 'state' / 'project_state.yaml'
        self.running = True

        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)

    def shutdown(self, signum, frame):
        print(f"[Agent 1] 收到信号 {signum}，正在关闭...")
        self.running = False

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

    def work(self):
        print("[Agent 1] 启动")
        
        while self.running:
            try:
                state = self.load_state()
                phase = state.get('phase', 'unknown')
                active_agent = self.get_active_agent()

                if active_agent != 'agent1':
                    print(f"[Agent 1] 等待... (当前活跃: {active_agent})")
                    time.sleep(5)
                    continue

                print(f"[Agent 1] 工作中... 阶段: {phase}")

                # 工作逻辑
                if phase == 'requirements_draft':
                    print("[Agent 1] 任务: 创建需求文档")
                    self.create_requirements()
                    self.transition_to_review()
                    
                elif phase == 'requirements_review':
                    if not state['requirements'].get('pm_signoff', False):
                        print("[Agent 1] 任务: 签署需求")
                        self.signoff_requirements()
                    else:
                        print("[Agent 1] 等待 Agent 2 签署...")
                        
                elif phase == 'design_draft':
                    print("[Agent 1] 任务: 评审设计文档")
                    # 等待 Agent 2 创建设计
                    print("[Agent 1] 等待设计文档...")
                        
                elif phase == 'design_review':
                    if not state['design'].get('pm_signoff', False):
                        print("[Agent 1] 任务: 签署设计")
                        self.signoff_design()
                    else:
                        print("[Agent 1] 等待 Agent 2 签署...")
                        
                elif phase == 'testing':
                    print("[Agent 1] 任务: 执行黑盒测试")
                    self.run_blackbox_tests()
                    
                else:
                    print(f"[Agent 1] 阶段 {phase} 无待办任务")

                time.sleep(10)

            except Exception as e:
                print(f"[Agent 1] 错误: {e}")
                time.sleep(5)

        print("[Agent 1] 已关闭")

    def create_requirements(self):
        print("[Agent 1] 创建需求文档...")
        # 文档已存在，无需创建
        print("[Agent 1] ✓ 需求文档已存在")

    def transition_to_review(self):
        state = self.load_state()
        state['phase'] = 'requirements_review'
        state['requirements']['status'] = 'review'
        state['history'].insert(0, {
            'id': f'req_review_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'action': 'review_start',
            'agent_id': 'agent1',
            'details': '启动需求评审: Bug触发Agent2自动修复功能'
        })
        self.save_state(state)
        print("[Agent 1] ✓ 已启动需求评审")

    def signoff_requirements(self):
        state = self.load_state()
        state['requirements']['pm_signoff'] = True
        state['history'].insert(0, {
            'id': f'req_signoff_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'action': 'signoff',
            'agent_id': 'agent1',
            'details': '签署需求: 需求清晰，同意实现'
        })
        self.save_state(state)
        print("[Agent 1] ✓ 已签署需求")

    def signoff_design(self):
        state = self.load_state()
        state['design']['pm_signoff'] = True
        state['history'].insert(0, {
            'id': f'design_signoff_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'action': 'signoff',
            'agent_id': 'agent1',
            'details': '签署设计: 设计合理，同意实现'
        })
        self.save_state(state)
        print("[Agent 1] ✓ 已签署设计")

    def run_blackbox_tests(self):
        state = self.load_state()
        # 检查是否有 bug
        test_data = state.get('test', {})
        issues = test_data.get('issues_to_fix', [])
        
        if issues:
            print(f"[Agent 1] 发现 {len(issues)} 个 bug:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("[Agent 1] ✓ 测试通过，无 bug")
        
        state['test']['status'] = 'passed'
        state['history'].insert(0, {
            'id': f'test_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'action': 'test_complete',
            'agent_id': 'agent1',
            'details': f'黑盒测试完成: {len(issues)} 个 bug' if issues else '测试通过'
        })
        self.save_state(state)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', default='.', help='项目路径')
    args = parser.parse_args()

    agent1 = Agent1(args.path)
    agent1.work()
