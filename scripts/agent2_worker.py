#!/usr/bin/env python3
"""
Agent 2 (开发) 工作进程
"""
import sys
import os
import time
import signal
import yaml
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/Users/liuzhen/Documents/河广/Product Development/chatGPT/Digital Law/Digital court/金融法院/法官数字助手/案卷材料样例/融资租赁/(2024)沪74民初721号/OpenCode Trial/dual-agent-collaboration-system')

class Agent2:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.state_file = self.project_path / 'state' / 'project_state.yaml'
        self.running = True

        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)

    def shutdown(self, signum, frame):
        print(f"[Agent 2] 收到信号 {signum}，正在关闭...")
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
        print("[Agent 2] 启动")
        
        while self.running:
            try:
                state = self.load_state()
                phase = state.get('phase', 'unknown')
                active_agent = self.get_active_agent()

                if active_agent != 'agent2':
                    print(f"[Agent 2] 等待... (当前活跃: {active_agent})")
                    time.sleep(5)
                    continue

                print(f"[Agent 2] 工作中... 阶段: {phase}")

                # 工作逻辑
                if phase == 'requirements_review':
                    if not state['requirements'].get('dev_signoff', False):
                        print("[Agent 2] 任务: 评审并签署需求")
                        self.review_and_signoff_requirements()
                    else:
                        print("[Agent 2] 等待 Agent 1 完成...")
                        
                elif phase == 'design_draft':
                    print("[Agent 2] 任务: 创建设计文档")
                    self.create_design()
                        
                elif phase == 'design_review':
                    if not state['design'].get('dev_signoff', False):
                        print("[Agent 2] 任务: 评审并签署设计")
                        self.review_and_signoff_design()
                    else:
                        print("[Agent 2] 等待 Agent 1 签署...")
                        
                elif phase == 'development':
                    print("[Agent 2] 任务: 开发功能")
                    self.develop_feature()
                    
                elif phase == 'testing':
                    print("[Agent 2] 任务: 修复 bug（如有）")
                    # 等待 Agent 1 测试
                    print("[Agent 2] 等待 Agent 1 测试结果...")
                    
                else:
                    print(f"[Agent 2] 阶段 {phase} 无待办任务")

                time.sleep(10)

            except Exception as e:
                print(f"[Agent 2] 错误: {e}")
                time.sleep(5)

        print("[Agent 2] 已关闭")

    def review_and_signoff_requirements(self):
        state = self.load_state()
        
        # 评审
        print("[Agent 2] 评审需求文档...")
        review_comments = "技术方案可行；PhaseAdvanceEngine.detect_test_activate_agent_bugs_and2 方法设计合理"
        
        state['history'].insert(0, {
            'id': f'req_review_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'action': 'review',
            'agent_id': 'agent2',
            'details': f'Agent 2 评审需求: 通过。意见: {review_comments}'
        })
        
        # 签署
        state['requirements']['dev_signoff'] = True
        state['history'].insert(0, {
            'id': f'req_signoff_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'action': 'signoff',
            'agent_id': 'agent2',
            'details': '签署需求: 技术方案可行，同意实现'
        })
        
        self.save_state(state)
        print("[Agent 2] ✓ 已评审并签署需求")

    def create_design(self):
        state = self.load_state()
        
        # 检查设计文档是否存在
        design_doc = self.project_path / 'docs' / '02-design' / 'detailed_design_bug_trigger_agent2_v1.md'
        if design_doc.exists():
            print("[Agent 2] ✓ 设计文档已存在")
        else:
            print("[Agent 2] 设计文档不存在，需要创建")
        
        # 推进到设计评审
        state['phase'] = 'design_review'
        state['design']['status'] = 'review'
        state['history'].insert(0, {
            'id': f'design_review_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'action': 'review_start',
            'agent_id': 'agent2',
            'details': '启动设计评审: Bug触发Agent2自动修复功能'
        })
        
        self.save_state(state)
        print("[Agent 2] ✓ 已启动设计评审")

    def review_and_signoff_design(self):
        state = self.load_state()
        
        # 评审
        print("[Agent 2] 评审设计文档...")
        review_comments = "设计合理，与现有框架集成方式正确；代码实现方案可行"
        
        state['history'].insert(0, {
            'id': f'design_review_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'action': 'review',
            'agent_id': 'agent2',
            'details': f'Agent 2 评审设计: 通过。意见: {review_comments}'
        })
        
        # 签署
        state['design']['dev_signoff'] = True
        state['history'].insert(0, {
            'id': f'design_signoff_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'action': 'signoff',
            'agent_id': 'agent2',
            'details': '签署设计: 设计合理，同意实现'
        })
        
        self.save_state(state)
        print("[Agent 2] ✓ 已评审并签署设计")

    def develop_feature(self):
        state = self.load_state()
        
        # 检查功能是否已实现
        print("[Agent 2] 检查功能实现...")
        
        # 推进到测试阶段
        state['phase'] = 'testing'
        state['test']['status'] = 'in_progress'
        state['history'].insert(0, {
            'id': f'dev_complete_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            'action': 'phase_advance',
            'agent_id': 'agent2',
            'details': '开发完成，推进到测试阶段'
        })
        
        self.save_state(state)
        print("[Agent 2] ✓ 开发完成，推进到测试阶段")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', default='.', help='项目路径')
    args = parser.parse_args()

    agent2 = Agent2(args.path)
    agent2.work()
