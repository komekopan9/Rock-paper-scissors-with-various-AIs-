from .janken_ai import PatternJankenAI

def get_user_hand():
    """ユーザーからの入力を取得"""
    while True:
        print("\n手を選んでください")
        print("1: ✊ グー")
        print("2: ✌️ チョキ")
        print("3: ✋ パー")
        print("q: 終了")
        print("選択: ", end="")
        user_input = input().strip().lower()
        
        if user_input == 'q':
            return None
            
        if user_input in ['1', '2', '3']:
            ai = PatternJankenAI()  # インスタンスを作成してマッピングにアクセス
            return ai.input_to_hand[user_input]
        else:
            print("無効な入力です。1から3の数字を入力するか、qで終了してください。")

def judge(ai_hand, user_hand):
    """勝敗を判定"""
    # 絵文字を除いた部分で比較
    ai_hand_plain = ai_hand.split()[-1]
    user_hand_plain = user_hand.split()[-1]
    
    if ai_hand_plain == user_hand_plain:
        return 'draw'
    elif (ai_hand_plain == 'グー' and user_hand_plain == 'チョキ') or \
         (ai_hand_plain == 'チョキ' and user_hand_plain == 'パー') or \
         (ai_hand_plain == 'パー' and user_hand_plain == 'グー'):
        return 'win'
    else:
        return 'lose'

def main():
    print("🎮 パターン認識じゃんけんAI スタート！")
    print("-----------------------------------")
    
    ai = PatternJankenAI()
    
    while True:
        # ユーザーの手を取得
        user_hand = get_user_hand()
        if user_hand is None:
            print("ゲームを終了します。")
            break
            
        # AIの手を決定
        ai_hand = ai.get_next_hand()
        
        # 勝敗を判定
        result = judge(ai_hand, user_hand)
        
        # 結果を表示
        print(f"\nあなた: {user_hand}")
        print(f"AI: {ai_hand}")
        
        if result == 'win':
            print("結果: 🤖 AIの勝ち")
        elif result == 'lose':
            print("結果: 🎉 あなたの勝ち")
        else:
            print("結果: 🤝 引き分け")
        
        # AIの状態を更新
        ai.last_hand = ai_hand
        ai.update_sequence(result)
        
        print("-----------------------------------")

if __name__ == "__main__":
    main()
