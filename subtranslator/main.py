import argparse
from subtranslator.tui import launch_tui

def main():
    parser = argparse.ArgumentParser(description="SubTranslator - AI-powered subtitle localization tool")
    parser.add_argument('--input', type=str, help='Input .srt subtitle file')
    parser.add_argument('--target-lang', type=str, help='Target language ISO 639-1 code')
    parser.add_argument('--censorship', action='store_true', help='Enable NSFW censorship')
    parser.add_argument('--batch', action='store_true', help='Run in headless batch mode')
    args = parser.parse_args()

    if args.batch:
        print("Batch mode not yet implemented.")
    else:
        launch_tui()

if __name__ == "__main__":
    main()
