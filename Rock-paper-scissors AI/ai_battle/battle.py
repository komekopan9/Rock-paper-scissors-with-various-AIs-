import random
import argparse
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# 親ディレクトリをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from bayesian_ai.janken_ai import JankenAI as BayesianAI
    from pattern_ai.janken_ai import PatternJankenAI as PatternAI
except ImportError as e:
    print(f"エラー: 必要なモジュールのインポートに失敗しました: {e}")
    print("プロジェクトのルートディレクトリが正しく設定されているか確認してください。")
    sys.exit(1)

class JankenBattle:
    def __init__(self, mode: str = 'aivsai', player_ai: str = 'pattern'):
        """じゃんけんバトルを初期化
        
        Args:
            mode: 対戦モード ('aivsai' または 'playervsai')
            player_ai: プレイヤーが対戦するAI ('bayesian' または 'pattern')
        """
        self.rounds_played = 0
        self.mode = mode
        self.player_ai = player_ai
        
        # AIを初期化
        self.bayesian_ai = BayesianAI(max_history=30, decay_start=20)
        self.pattern_ai = PatternAI()
        
        # 対戦モードに応じてAIを設定
        if mode == 'aivsai':
            self.ai1 = self.bayesian_ai
            self.ai2 = self.pattern_ai
        else:  # playervsai
            if player_ai == 'bayesian':
                self.ai1 = self.pattern_ai  # プレイヤーは常にai1、対戦AIはai2
                self.ai2 = self.bayesian_ai
            else:
                self.ai1 = self.bayesian_ai
                self.ai2 = self.pattern_ai
        
        self.scores = {'player': 0, 'ai': 0, 'draw': 0} if mode == 'playervsai' else {'ai1': 0, 'ai2': 0, 'draw': 0}
        self.history = []
    
    def judge(self, hand1: str, hand2: str) -> str:
        """勝敗を判定
        
        Args:
            hand1: 1つ目の手
            hand2: 2つ目の手
            
        Returns:
            str: 勝敗結果 ('player', 'ai', 'draw' または 'ai1', 'ai2', 'draw')
        """
        # 絵文字を除いた部分で比較
        hand1_plain = hand1.split()[-1]
        hand2_plain = hand2.split()[-1]
        
        if hand1_plain == hand2_plain:
            return 'draw'
            
        if (hand1_plain == 'グー' and hand2_plain == 'チョキ') or \
           (hand1_plain == 'チョキ' and hand2_plain == 'パー') or \
           (hand1_plain == 'パー' and hand2_plain == 'グー'):
            return 'player' if self.mode == 'playervsai' else 'ai1'
        else:
            return 'ai' if self.mode == 'playervsai' else 'ai2'
    
    def play_round(self):
        """1ラウンド対戦"""
        # AI1（ベイズ推論）の手を予測
        ai1_hand = self.ai1.predict_next_hand()
        
        # AI2（パターン認識）の手を予測
        ai2_hand = self.ai2.get_next_hand()
        
        # 勝敗を判定
        result = self.judge(ai1_hand, ai2_hand)
        
        # スコアを更新
        self.scores[result] += 1
        
        # 履歴に記録
        self.history.append({
            'ai1_hand': ai1_hand,
            'ai2_hand': ai2_hand,
            'result': result
        })
        
        # AIに結果を学習させる
        self.ai1.update_model(ai2_hand)  # AI1はAI2の手を学習
        self.ai2.last_hand = ai2_hand    # AI2は自分の手を記録
        
        # 勝敗に応じてAI2のシーケンスを更新
        if result == 'ai1':
            self.ai2.update_sequence('lose')
        elif result == 'ai2':
            self.ai2.update_sequence('win')
        else:
            self.ai2.update_sequence('draw')
        
        return result, ai1_hand, ai2_hand
    
    def print_result(self, round_num: int, result: str, hand1: str, hand2: str) -> None:
        """結果を表示
        
        Args:
            round_num: ラウンド番号
            result: 勝敗結果
            hand1: 1つ目の手
            hand2: 2つ目の手
        """
        print(f"\n--- ラウンド {round_num} ---")
        
        if self.mode == 'playervsai':
            print(f"あなた: {hand1}")
            ai_name = "ベイズAI" if self.player_ai == 'bayesian' else "パターンAI"
            print(f"{ai_name}: {hand2}")
            
            if result == 'draw':
                print("結果: 引き分け")
            elif result == 'player':
                print("結果: あなたの勝ち！")
            else:
                print(f"結果: {ai_name}の勝ち！")
        else:  # AI vs AIモード
            print(f"ベイズAI: {hand1 if hasattr(self.ai1, 'predict_next_hand') else hand2}")
            print(f"パターンAI: {hand2 if hasattr(self.ai2, 'get_next_hand') else hand1}")
            
            if result == 'draw':
                print("結果: 引き分け")
            else:
                winner = "ベイズAI" if result == 'ai1' else "パターンAI"
                print(f"結果: {winner}の勝ち！")
    
    def print_summary(self) -> None:
        """対戦のサマリーを表示"""
        print("\n=== 現在の戦績 ===")
        print(f"総ラウンド数: {self.rounds_played}")
        
        if self.mode == 'playervsai':
            ai_name = "ベイズAI" if self.player_ai == 'bayesian' else "パターンAI"
            print(f"あなたの勝利: {self.scores['player']}回")
            print(f"{ai_name}の勝利: {self.scores['ai']}回")
            print(f"引き分け: {self.scores['draw']}回")
            
            if self.scores['player'] > self.scores['ai']:
                print("\n🎉 あなたがリードしています！")
            elif self.scores['ai'] > self.scores['player']:
                print(f"\n😢 {ai_name}がリードしています...")
            else:
                print("\n🤝 現在は引き分けです")
        else:  # AI vs AIモード
            print(f"ベイズAIの勝利: {self.scores['ai1']}回")
            print(f"パターンAIの勝利: {self.scores['ai2']}回")
            print(f"引き分け: {self.scores['draw']}回")
            
            if self.scores['ai1'] > self.scores['ai2']:
                print("\n🎉 現在のリーダー: ベイズAI")
            elif self.scores['ai2'] > self.scores['ai1']:
                print("\n🎉 現在のリーダー: パターンAI")
            else:
                print("\n🤝 現在は引き分けです")
    
    def get_player_hand(self) -> str:
        """プレイヤーの手を取得
        
        Returns:
            str: プレイヤーの手、またはNone（中断時）
        """
        while True:
            print("\n手を選んでください:")
            print("1: グー")
            print("2: チョキ")
            print("3: パー")
            print("0: 対戦を中断")
            choice = input("選択してください (0-3): ")
            
            if choice == '0':
                return None  # 中断を表す
                
            if choice in ['1', '2', '3']:
                hands = {
                    '1': '✊ グー',
                    '2': '✌️ チョキ',
                    '3': '✋ パー'
                }
                return hands[choice]
                
            print("無効な入力です。0から3の数字を入力してください。")

    def play_round(self) -> Tuple[str, str, str]:
        """1ラウンド対戦して結果を返す
        
        Returns:
            Tuple[result, hand1, hand2]: 勝敗結果と両者の手
            or None: プレイヤーが中断を選択した場合
        """
        if self.mode == 'playervsai':
            # プレイヤー vs AIモード
            player_hand = self.get_player_hand()
            if player_hand is None:  # プレイヤーが中断を選択
                return None, None, None
                
            ai_hand = self.ai2.get_next_hand() if hasattr(self.ai2, 'get_next_hand') else self.ai2.predict_next_hand()
            
            # 勝敗を判定
            result = self.judge(player_hand, ai_hand)
            
            # スコアを更新
            self.scores[result] += 1
            self.rounds_played += 1
            
            # 履歴に記録
            self.history.append({
                'player_hand': player_hand,
                'ai_hand': ai_hand,
                'result': result
            })
            
            # AIに結果を学習させる
            if hasattr(self.ai2, 'update_model'):
                self.ai2.update_model(player_hand)
            if hasattr(self.ai2, 'last_hand'):
                self.ai2.last_hand = ai_hand
            
            # 勝敗に応じてAIのシーケンスを更新
            if hasattr(self.ai2, 'update_sequence'):
                if result == 'player':
                    self.ai2.update_sequence('lose')
                elif result == 'ai':
                    self.ai2.update_sequence('win')
                else:
                    self.ai2.update_sequence('draw')
            
            return result, player_hand, ai_hand
            
        else:  # AI vs AIモード
            # AI1の手を予測
            ai1_hand = self.ai1.predict_next_hand() if hasattr(self.ai1, 'predict_next_hand') else self.ai1.get_next_hand()
            
            # AI2の手を予測
            ai2_hand = self.ai2.get_next_hand() if hasattr(self.ai2, 'get_next_hand') else self.ai2.predict_next_hand()
            
            # 勝敗を判定
            result = self.judge(ai1_hand, ai2_hand)
            
            # スコアを更新
            self.scores[result] += 1
            self.rounds_played += 1
            
            # 履歴に記録
            self.history.append({
                'ai1_hand': ai1_hand,
                'ai2_hand': ai2_hand,
                'result': result
            })
            
            # AIに結果を学習させる
            if hasattr(self.ai1, 'update_model'):
                self.ai1.update_model(ai2_hand)
            if hasattr(self.ai2, 'update_model'):
                self.ai2.update_model(ai1_hand)
                
            if hasattr(self.ai1, 'last_hand'):
                self.ai1.last_hand = ai1_hand
            if hasattr(self.ai2, 'last_hand'):
                self.ai2.last_hand = ai2_hand
            
            # 勝敗に応じてAIのシーケンスを更新
            if hasattr(self.ai1, 'update_sequence'):
                if result == 'ai1':
                    self.ai1.update_sequence('win')
                elif result == 'ai2':
                    self.ai1.update_sequence('lose')
                else:
                    self.ai1.update_sequence('draw')
                    
            if hasattr(self.ai2, 'update_sequence'):
                if result == 'ai2':
                    self.ai2.update_sequence('win')
                elif result == 'ai1':
                    self.ai2.update_sequence('lose')
                else:
                    self.ai2.update_sequence('draw')
            
            return result, ai1_hand, ai2_hand

def print_main_menu() -> str:
    """メインメニューを表示"""
    print("\n=== AIじゃんけんバトル ===")
    print("1: AI vs AI 対戦モード")
    print("2: プレイヤー vs AI 対戦モード")
    print("0: 終了")
    return input("モードを選択してください (0-2): ")

def print_ai_selection_menu() -> str:
    """AI選択メニューを表示"""
    print("\n対戦するAIを選択してください:")
    print("1: ベイズAI (確率的な推論で手を決める)")
    print("2: パターンAI (過去の手のパターンを分析)")
    return input("選択してください (1-2): ")

def print_battle_menu(mode: str) -> str:
    """バトルメニューを表示
    
    Args:
        mode: 対戦モード ('aivsai' または 'playervsai')
    """
    if mode == 'aivsai':
        print("\n=== AI vs AI モード ===")
    else:
        print("\n=== プレイヤー vs AI モード ===")
        
    print("1: 10回連続対戦")
    print("2: 1回ずつ対戦")
    print("3: 無制限対戦 (0で中断)")
    print("4: 現在のスコアを表示")
    print("0: メインメニューに戻る")
    return input("選択してください (0-4): ")

def main():
    """メインのゲームループ"""
    battle = None
    
    while True:
        # メインメニューを表示
        choice = print_main_menu()
        
        if choice == '1':  # AI vs AI モード
            battle = JankenBattle(mode='aivsai')
            battle_loop(battle, 'aivsai')
            
        elif choice == '2':  # プレイヤー vs AI モード
            # AIを選択
            ai_choice = print_ai_selection_menu()
            if ai_choice in ['1', '2']:
                ai_type = 'bayesian' if ai_choice == '1' else 'pattern'
                battle = JankenBattle(mode='playervsai', player_ai=ai_type)
                battle_loop(battle, 'playervsai')
            else:
                print("無効な選択です。")
                
        elif choice == '0':  # 終了
            print("\nゲームを終了します。お疲れ様でした！")
            break
            
        else:
            print("\n無効な選択です。もう一度選択してください。")

def battle_loop(battle, mode: str) -> None:
    """バトルループを実行
    
    Args:
        battle: JankenBattle インスタンス
        mode: 対戦モード ('aivsai' または 'playervsai')
    """
    while True:
        choice = print_battle_menu(mode)
        
        if choice == '1':  # 10回連続対戦
            for _ in range(10):
                result, hand1, hand2 = battle.play_round()
                battle.print_result(battle.rounds_played, result, hand1, hand2)
            
        elif choice == '2':  # 1回ずつ対戦
            result, hand1, hand2 = battle.play_round()
            battle.print_result(battle.rounds_played, result, hand1, hand2)
        
        elif choice == '3':  # 無制限対戦
            print("\n無制限対戦を開始します。")
            round_count = 0
            while True:
                round_count += 1
                print(f"\n--- ラウンド {round_count} ---")
                
                # 対戦を実行
                result, hand1, hand2 = battle.play_round()
                
                # プレイヤーが中断を選択した場合
                if result is None and hand1 is None and hand2 is None:
                    print("\n対戦を中断します。")
                    battle.print_summary()
                    break
                    
                battle.print_result(round_count, result, hand1, hand2)
                
                # AI vs AIモードの場合は継続確認
                if mode != 'playervsai':
                    print("\n0を入力で中断、Enterで続行")
                    if input("選択: ") == '0':
                        print("\n対戦を中断します。")
                        battle.print_summary()
                        break
        
        elif choice == '4':  # 現在のスコアを表示
            battle.print_summary()
        
        elif choice == '0':  # メインメニューに戻る
            print("\nメインメニューに戻ります。")
            break
            
        else:
            print("\n無効な選択です。もう一度選択してください。")

if __name__ == "__main__":
    main()
