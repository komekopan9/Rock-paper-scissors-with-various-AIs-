import random

class PatternJankenAI:
    def __init__(self):
        # 手の定義
        self.hands = ['✊ グー', '✌️ チョキ', '✋ パー']
        self.hand_to_num = {'✊ グー': 0, '✌️ チョキ': 1, '✋ パー': 2}
        self.num_to_hand = {0: '✊ グー', 1: '✌️ チョキ', 2: '✋ パー'}
        self.input_to_hand = {'1': '✊ グー', '2': '✌️ チョキ', '3': '✋ パー'}
        
        # 状態管理
        self.last_hand = None
        self.last_result = None  # 'win', 'lose', 'draw'
        self.sequence = []
        
    def get_next_hand(self):
        """次の手を決定する"""
        if not self.sequence:
            # シーケンスが空の場合はランダムに手を選ぶ
            return random.choice(self.hands)
            
        # シーケンスに従って手を選ぶ
        next_hand = self.sequence.pop(0)
        return next_hand
    
    def update_sequence(self, result):
        """勝敗結果に基づいて次の手のシーケンスを更新
        
        Args:
            result: 前回の結果 ('win', 'lose', 'draw')
        """
        if result == 'win':
            # 勝った場合のシーケンス: グー → チョキ → パー → グー → ...
            self.sequence = [
                self.num_to_hand[(self.hand_to_num[self.last_hand] + 1) % 3],  # チョキ
                self.num_to_hand[(self.hand_to_num[self.last_hand] - 1) % 3],  # パー
                self.num_to_hand[self.hand_to_num[self.last_hand]]             # グー
            ]
        elif result == 'lose':
            # 負けた場合のシーケンス: グー → パー → チョキ → グー → ...
            self.sequence = [
                self.num_to_hand[(self.hand_to_num[self.last_hand] - 1) % 3],  # パー
                self.num_to_hand[(self.hand_to_num[self.last_hand] + 1) % 3],  # チョキ
                self.num_to_hand[self.hand_to_num[self.last_hand]]             # グー
            ]
        # 引き分けの場合はシーケンスをリセット
        else:
            self.sequence = []
