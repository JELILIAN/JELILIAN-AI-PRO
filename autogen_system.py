#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微软AutoGen多智能体协作系统
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class AutoGenAgent:
    """AutoGen智能体基类"""
    
    def __init__(self, name: str, role: str, system_message: str):
        self.name = name
        self.role = role
        self.system_message = system_message
        self.conversation_history = []
    
    async def generate_response(self, message: str, context: Dict = None) -> str:
        """生成响应"""
        try:
            from app.llm import LLM
            llm = LLM()
            
            # 构建上下文消息
            messages = [{"role": "system", "content": self.system_message}]
            
            # 添加对话历史
            for msg in self.conversation_history[-5:]:  # 保留最近5轮对话
                messages.append(msg)
            
            # 添加当前消息
            messages.append({"role": "user", "content": message})
            
            response = await llm.ask(messages)
            
            # 记录对话历史
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            return f"智能体 {self.name} 响应错误: {str(e)}"

class AutoGenOrchestrator:
    """AutoGen协调器 - 管理多智能体协作"""
    
    def __init__(self):
        self.agents = {}
        self.conversation_flow = []
        self.setup_agents()
    
    def setup_agents(self):
        """设置多个专业智能体"""
        
        # 1. 分析师智能体
        self.agents['analyst'] = AutoGenAgent(
            name="分析师",
            role="数据分析和研究专家",
            system_message="""你是一个专业的数据分析师和研究专家。你的职责是：
1. 深入分析用户提出的问题
2. 识别关键信息和数据需求
3. 提供专业的分析视角
4. 为其他智能体提供分析基础

请用专业、准确的语言回应，重点关注数据和事实。"""
        )
        
        # 2. 创意师智能体
        self.agents['creative'] = AutoGenAgent(
            name="创意师",
            role="创意设计和内容创作专家",
            system_message="""你是一个富有创意的设计师和内容创作专家。你的职责是：
1. 提供创新的解决方案
2. 设计吸引人的内容和方案
3. 从创意角度优化建议
4. 让复杂的概念变得易懂有趣

请用生动、有创意的语言回应，注重用户体验和视觉效果。"""
        )
        
        # 3. 技术专家智能体
        self.agents['technical'] = AutoGenAgent(
            name="技术专家",
            role="技术实现和架构专家",
            system_message="""你是一个资深的技术专家和架构师。你的职责是：
1. 提供技术实现方案
2. 评估技术可行性
3. 优化系统架构和性能
4. 解决技术难题

请用准确、专业的技术语言回应，重点关注实现细节和最佳实践。"""
        )
        
        # 4. 产品经理智能体
        self.agents['product'] = AutoGenAgent(
            name="产品经理",
            role="产品策略和用户体验专家",
            system_message="""你是一个经验丰富的产品经理。你的职责是：
1. 从用户需求角度分析问题
2. 平衡各方面的建议和约束
3. 提供产品化的解决方案
4. 确保方案的可行性和用户价值

请用清晰、实用的语言回应，重点关注用户价值和商业可行性。"""
        )
        
        # 5. 协调者智能体
        self.agents['coordinator'] = AutoGenAgent(
            name="协调者",
            role="多智能体协调和总结专家",
            system_message="""你是多智能体团队的协调者。你的职责是：
1. 整合各个智能体的建议
2. 识别共识和分歧
3. 提供综合性的解决方案
4. 确保回答的完整性和一致性

请用综合、平衡的语言回应，整合所有智能体的优秀建议。"""
        )
    
    async def process_with_multi_agents(self, user_message: str, selected_agents: List[str] = None) -> Dict[str, Any]:
        """使用多智能体处理用户消息"""
        
        if selected_agents is None:
            selected_agents = ['analyst', 'creative', 'technical', 'product']
        
        # 第一阶段：各智能体独立分析
        agent_responses = {}
        
        for agent_name in selected_agents:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                try:
                    response = await agent.generate_response(user_message)
                    agent_responses[agent_name] = {
                        'agent': agent.name,
                        'role': agent.role,
                        'response': response
                    }
                except Exception as e:
                    agent_responses[agent_name] = {
                        'agent': agent.name,
                        'role': agent.role,
                        'response': f"处理错误: {str(e)}"
                    }
        
        # 第二阶段：协调者整合所有建议
        coordinator = self.agents['coordinator']
        
        # 构建协调者的输入
        coordination_input = f"""用户问题: {user_message}

各智能体的分析结果：
"""
        
        for agent_name, response_data in agent_responses.items():
            coordination_input += f"""
{response_data['agent']} ({response_data['role']}):
{response_data['response']}
---
"""
        
        coordination_input += """
请整合以上所有智能体的建议，提供一个综合、完整、实用的解决方案。"""
        
        try:
            final_response = await coordinator.generate_response(coordination_input)
        except Exception as e:
            final_response = f"协调整合时出现错误: {str(e)}"
        
        return {
            'user_message': user_message,
            'agent_responses': agent_responses,
            'final_response': final_response,
            'timestamp': datetime.now().isoformat(),
            'agents_used': selected_agents
        }
    
    async def get_smart_recommendations(self, conversation_history: List[Dict]) -> List[str]:
        """基于对话历史生成智能推荐问题"""
        
        # 分析对话历史，生成相关推荐
        if not conversation_history:
            return [
                "请帮我分析当前AI技术的发展趋势",
                "如何设计一个用户友好的产品界面？",
                "请为我的项目提供技术架构建议",
                "如何制定有效的产品发展策略？"
            ]
        
        # 基于最后一次对话生成推荐
        last_message = conversation_history[-1].get('content', '')
        
        analyst = self.agents['analyst']
        recommendation_prompt = f"""基于用户的最后一个问题："{last_message}"
        
请生成4个相关的后续问题建议，这些问题应该：
1. 与用户的兴趣相关
2. 能够深入探讨相关话题
3. 具有实用价值
4. 适合多智能体协作分析

请只返回4个问题，每行一个，不要其他解释。"""
        
        try:
            recommendations_text = await analyst.generate_response(recommendation_prompt)
            recommendations = [line.strip() for line in recommendations_text.split('\n') if line.strip()]
            return recommendations[:4]  # 确保只返回4个
        except:
            return [
                "请深入分析这个话题的相关方面",
                "如何将这个概念应用到实际项目中？",
                "这个领域还有哪些值得探索的方向？",
                "如何优化和改进现有的解决方案？"
            ]

# 全局AutoGen系统实例
autogen_system = AutoGenOrchestrator()