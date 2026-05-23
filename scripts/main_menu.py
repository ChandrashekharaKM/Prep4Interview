"""
scripts/main_menu.py
Extended SwipeGen main menu — existing automation preserved, AI Assistant added as optional entry.
"""

import os
import sys


def print_banner():
    print("\n" + "=" * 50)
    print("     SwipeGen HR Automation Suite")
    print("=" * 50)


def main_menu():
    print_banner()
    print("""
  [1] Generate offer letters (batch)
  [2] Send onboarding emails
  [3] Export HR reports
  [4] Update employee records
  ──────────────────────────────────
  [5] 🤖  AI Assistant (HR-Copilot)      ← NEW
  ──────────────────────────────────
  [0] Exit
""")
    choice = input("  Enter choice: ").strip()
    return choice


def launch_ai_assistant():
    """Launch the HR-Copilot Streamlit UI."""
    print("\n🤖 Launching HR-Copilot AI Assistant...")
    print("   (Streamlit UI will open at http://localhost:8501)\n")
    os.system(f"{sys.executable} -m streamlit run frontend/app.py")


def run():
    while True:
        choice = main_menu()
        if choice == "0":
            print("\nGoodbye!\n")
            break
        elif choice == "1":
            print("\n[Stub] Batch offer letter generation — existing SwipeGen logic here")
        elif choice == "2":
            print("\n[Stub] Onboarding email send — existing SwipeGen logic here")
        elif choice == "3":
            print("\n[Stub] HR report export — existing SwipeGen logic here")
        elif choice == "4":
            print("\n[Stub] Employee record update — existing SwipeGen logic here")
        elif choice == "5":
            launch_ai_assistant()
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    run()
