from .janken_ai import JankenAI

def get_user_hand():
    """ユーザーからの入力を取得"""
    hand_mapping = {
        '1': '✊ グー',
        '2': '✌️ チョキ',
        '3': '✋ パー'
    }
    
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
            
        if user_input in hand_mapping:
            return hand_mapping[user_input]
        else:
            print("無効な入力です。1から3の数字を入力するか、qで終了してください。")

def judge(ai_hand, user_hand):
    """勝敗を判定"""
    # 絵文字を除いた部分で比較
    ai_hand_plain = ai_hand.split()[-1]
    user_hand_plain = user_hand.split()[-1]
    
    if ai_hand_plain == user_hand_plain:
        return "🤝 引き分け"
    elif (ai_hand_plain == 'グー' and user_hand_plain == 'チョキ') or \
         (ai_hand_plain == 'チョキ' and user_hand_plain == 'パー') or \
         (ai_hand_plain == 'パー' and user_hand_plain == 'グー'):
        return "🤖 AIの勝ち"
    else:
        return "🎉 あなたの勝ち"

def main():
    print("🎮 ベイズ推論じゃんけんAI スタート！")
    print("-----------------------------------")
    
    ai = JankenAI()
    
    while True:
        # ユーザーの手を取得
        user_hand = get_user_hand()
        if user_hand is None:
            print("ゲームを終了します。")
            break
            
        # AIの手を決定
        ai_hand = ai.predict_next_hand()
        
        # 結果を表示
        print(f"\nあなた: {user_hand}")
        print(f"AI: {ai_hand}")
        print(f"結果: {judge(ai_hand, user_hand)}")
        
        # モデルを更新
        ai.update_model(user_hand)
        
        print("-----------------------------------")

if __name__ == "__main__":
    main()
