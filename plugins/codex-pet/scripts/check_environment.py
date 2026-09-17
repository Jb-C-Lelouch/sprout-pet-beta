"""Check a beta installation without reading or modifying the user's save."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile


def check(smoke=False):
    if sys.version_info < (3, 10):
        raise RuntimeError('Python 3.10 or newer is required.')
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    try:
        asset = Path(__file__).resolve().parents[1] / 'assets/pixel/garden.png'
        image = tk.PhotoImage(master=root, data=asset.read_bytes())
        if image.width() < 1:
            raise RuntimeError('Garden image is empty.')
        print('PASS: Python, Tk and garden image')
        print('Codex CLI: ' + ('found' if shutil.which('codex') else 'not on PATH; needed for CLI installation'))
        if smoke:
            import pet
            import garden
            from desktop_scene import GardenScene
            with tempfile.TemporaryDirectory(prefix='sprout-beta-check-') as temporary:
                directory = Path(temporary)
                with pet.connect(directory) as db:
                    pet.tick(db)
                    garden.edit(db, 'plant', 1, 'clover')
                    before = garden.snapshot(db)
                db.close()
                with pet.connect(directory) as db:
                    assert garden.snapshot(db)['plots'] == before['plots']
                    session = 'beta-smoke'
                    transcript = directory / 'test.jsonl'
                    def usage(total):
                        transcript.write_text('\n'.join(json.dumps(row) for row in [
                            {'type': 'session_meta', 'payload': {'id': session}},
                            {'type': 'event_msg', 'payload': {'type': 'token_count', 'info':
                                {'total_token_usage': {'total_tokens': total}}}}
                        ]), encoding='utf-8')
                    event = dict(session_id=session, transcript_path=str(transcript))
                    usage(100)
                    pet.handle(db, dict(event, hook_event_name='SessionStart'))
                    usage(1100)
                    pet.handle(db, dict(event, hook_event_name='Stop'))
                    assert pet.status(db)['credited_tokens'] == 1000
                    pet.handle(db, dict(event, hook_event_name='Stop'))
                    assert pet.status(db)['credited_tokens'] == 1000
                db.close()
                scene = GardenScene(root, directory)
                root.withdraw()
                root.update()
                assert scene.data is not None
                scene.close()
            print('PASS: isolated save/reopen, synthetic token hooks, duplicate protection, garden render')
    finally:
        try:
            root.destroy()
        except tk.TclError:
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke', action='store_true', help='Use a temporary save for a synthetic integration check')
    args = parser.parse_args()
    try:
        check(args.smoke)
    except Exception as exc:
        print('FAILED: ' + str(exc), file=sys.stderr)
        sys.exit(1)
