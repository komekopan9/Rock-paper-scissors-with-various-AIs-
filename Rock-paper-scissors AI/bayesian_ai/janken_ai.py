import numpy as np
from collections import defaultdict, deque
import random

class JankenAI:
    def __init__(self, max_history=50, decay_start=40):
        """
        初期化
        
        Args:
            max_history: 保持する最大履歴数
            decay_start: 重みの減衰を開始するインデックス
        """
        # 手の定義（絵文字付き）
        self.hands = ['✊ グー', '✌️ チョキ', '✋ パー']
        self.hand_to_num = {'✊ グー': 0, '✌️ チョキ': 1, '✋ パー': 2}
        self.num_to_hand = {0: '✊ グー', 1: '✌️ チョキ', 2: '✋ パー'}
        self.input_to_hand = {'1': '✊ グー', '2': '✌️ チョキ', '3': '✋ パー'}
        
        # マルコフ連鎖の遷移確率を保持する辞書
        # transition_counts[(prev_hand, current_hand)] = 重み付き出現回数
        self.transition_counts = defaultdict(lambda: defaultdict(float))
        
        # 履歴を保持するキュー
        self.history = deque(maxlen=max_history)
        self.max_history = max_history
        self.decay_start = decay_start
        
        # 直前の手を記録
        self.last_hand = None
        
    def _calculate_weight(self, index):
        """インデックスに基づいて重みを計算
        
        Args:
            index: 履歴内のインデックス（0から開始）
            
        Returns:
            float: 計算された重み（0.0 〜 1.0）
        """
        if index < self.decay_start:
            return 1.0
        # 20件目から30件目にかけて重みを1.0から0.0まで直線的に減少
        weight = 1.0 - (index - self.decay_start + 1) / (self.max_history - self.decay_start + 1)
        return max(0.0, weight)
    
    def update_model(self, user_hand):
        """ユーザーの手を学習データとしてモデルを更新
        
        Args:
            user_hand: ユーザーの手（文字列または数値インデックス）
        """
        # 手の形式を統一（数値インデックスの場合は文字列に変換）
        if isinstance(user_hand, int) and 0 <= user_hand <= 2:
            user_hand = self.num_to_hand[user_hand]
        elif user_hand in ['0', '1', '2']:
            user_hand = self.num_to_hand[int(user_hand)]
        elif user_hand in self.input_to_hand:
            user_hand = self.input_to_hand[user_hand]
            
        # 手が有効でない場合は無視
        if user_hand not in self.hand_to_num:
            return
        
        # 履歴に追加
        if self.last_hand is not None:
            self.history.append((self.last_hand, user_hand))
            
            # 遷移確率を更新
            # 古い遷移確率をリセット
            self.transition_counts = defaultdict(lambda: defaultdict(float))
            
            # 履歴を元に重み付きで遷移確率を再計算
            for i, (prev, curr) in enumerate(self.history):
                weight = self._calculate_weight(i)
                self.transition_counts[prev][curr] += weight
        
        self.last_hand = user_hand
    
    def predict_next_hand(self):
        """ユーザーの次の手を予測
        
        Returns:
            str: 予測に基づいた手（絵文字付き）
        """
        if self.last_hand is None or not self.transition_counts[self.last_hand]:
            # 十分なデータがない場合はランダムに選択
            return random.choice(self.hands)
            
        try:
            # 直前の手から次に出そうな手を予測
            next_hand_probs = self.transition_counts[self.last_hand]
            if not next_hand_probs:
                return random.choice(self.hands)
                
            # 最も確率の高い手を選択
            next_hand = max(next_hand_probs.items(), key=lambda x: x[1])[0]
            
            # 予測した手に勝つ手を選択
            predicted_hand_num = self.hand_to_num[next_hand]
            # グー(0) < パー(2), チョキ(1) < グー(0), パー(2) < チョキ(1)
            winning_hand_num = (predicted_hand_num - 1) % 3
            return self.num_to_hand[winning_hand_num]
            
        except Exception as e:
            # エラーが発生した場合はランダムな手を返す
            return random.choice(self.hands)
            
    def get_history_info(self):
        """現在の履歴情報を取得（デバッグ用）"""
        return {
            'history_size': len(self.history),
            'recent_weights': [self._calculate_weight(i) for i in range(min(10, len(self.history)))] if self.history else []
        }
