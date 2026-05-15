#!/usr/bin/env python3
"""
RTS Game Live Debug Controller (Reference Implementation)

This is a real-world example of extending LiveDebugController for a
complex Phaser 3 RTS game (Neon Dominion).

It demonstrates how to build high-level game-specific helpers on top
of the generic controller, including the new tracing and video features.

Usage:
    python -m examples.rts_game.rts_controller

    # Then in the REPL:
    ctrl.create_lobby("Test Game", 4)
    ctrl.add_ai_players(3, "swarm")
    ctrl.select_race("tech")
    ctrl.start_match()
    print(ctrl.get_game_state_summary())
"""

from __future__ import annotations

import code
import time
from pathlib import Path
from typing import Any, Optional

from controllers.live_debug_controller import LiveDebugController


class RTSLiveController(LiveDebugController):
    """High-level controller specialized for the Neon Dominion RTS game.

    Inherits robust CDP discovery, tracing, and video recording from the base class.
    """

    def __init__(
        self,
        cdp_url: str = "http://127.0.0.1:9222",
        fresh_context: bool = False,
        record_video: bool = False,
        video_dir: str = "recordings/rts",
    ):
        super().__init__(
            cdp_url=cdp_url,
            fresh_context=fresh_context,
            record_video=record_video,
            video_dir=video_dir,
        )
        self.lobby_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Lobby & Match Flow (high-level, hides all DOM details)
    # ------------------------------------------------------------------

    def create_lobby(self, name: str = "Autonomous Test", max_players: int = 4):
        """Create a new lobby."""
        print(f"[RTS] Creating lobby '{name}' (max {max_players})...")
        self.goto("http://localhost:5000")
        self.wait_for_selector("#create-lobby-btn", timeout=15000)
        self.click("#create-lobby-btn")
        self.wait_for_selector("#lobby-name", timeout=8000)
        self.fill("#lobby-name", name)

        try:
            self.fill("#max-players", str(max_players))
        except Exception:
            pass

        self.click("#confirm-create-lobby")
        time.sleep(1.2)
        print("[RTS] Lobby created")

    def add_ai_players(self, count: int = 1, race: str = "swarm"):
        """Add AI opponents to the current lobby."""
        print(f"[RTS] Adding {count} AI player(s) with race={race}...")
        for i in range(count):
            try:
                self.click("#add-ai-btn", timeout=5000)
                time.sleep(0.4)
                if self.is_visible("#ai-race-select"):
                    self.fill("#ai-race-select", race)
                    self.click("#confirm-add-ai")
            except Exception as e:
                print(f"  Warning: could not add AI #{i+1}: {e}")
        time.sleep(0.8)

    def select_race(self, race: str):
        """Select your race in the lobby (swarm, tech, etc.)."""
        print(f"[RTS] Selecting race: {race}")
        try:
            selector = f"[data-race='{race}']" if race else ".race-option"
            self.click(selector, timeout=6000)
        except Exception:
            self.click(f"button:has-text('{race.capitalize()}')", timeout=4000)
        time.sleep(0.6)

    def start_match(self):
        """Start the match from the lobby."""
        print("[RTS] Starting match...")
        self.click("#start-match-btn", timeout=10000)
        self.wait_for_selector(".game-scene, canvas", timeout=20000)
        print("[RTS] Match started!")

    def leave_match(self):
        """Leave the current match and return to lobby."""
        print("[RTS] Leaving match...")
        try:
            self.click("#leave-match-btn", timeout=5000)
        except Exception:
            self.click("button:has-text('Leave')", timeout=4000)
        time.sleep(1.5)

    # ------------------------------------------------------------------
    # Game State Inspection
    # ------------------------------------------------------------------

    def get_game_state_summary(self) -> dict[str, Any]:
        """Evaluate JavaScript in the Phaser game to get a high-level state snapshot."""
        js = """
        () => {
            const scene = window.game?.scene?.getScene('GameScene');
            if (!scene) return { error: 'No GameScene' };

            return {
                tick: scene.lastSnapshotTick || 0,
                players: Object.keys(scene.players || {}),
                myUnits: (scene.myUnits || []).length,
                visibleUnits: (scene.visibleUnits || []).length,
                resources: scene.resources || {},
                cameraZoom: scene.cameras?.main?.zoom || 1
            };
        }
        """
        try:
            return self.evaluate(js)
        except Exception as e:
            return {"error": str(e)}

    def take_screenshot(self, name: str = "rts") -> str:
        """Take a timestamped screenshot of the current game view."""
        path = f"/tmp/rts-{name}-{int(time.time())}.png"
        return super().screenshot(path, full_page=False)

    # ------------------------------------------------------------------
    # High-level debugging workflow helpers (new)
    # ------------------------------------------------------------------

    def record_full_game(
        self,
        name: str = "full-game",
        duration_seconds: int = 60,
    ) -> dict[str, Any]:
        """Convenience method: start tracing + video, play for a while, then stop."""
        trace_name = f"{name}-{int(time.time())}"

        print(f"[RTS] Starting full game recording: {trace_name}")
        self.start_tracing(trace_name, screenshots=True, snapshots=True, sources=True)

        if self.record_video:
            self.start_video_recording()

        print(f"[RTS] Letting game run for {duration_seconds}s...")
        time.sleep(duration_seconds)

        trace_path = self.stop_tracing()
        video_path = self.stop_video_recording()

        return {
            "trace": trace_path,
            "video": video_path,
            "duration": duration_seconds,
        }

    # ------------------------------------------------------------------
    # Help
    # ------------------------------------------------------------------

    def help(self):
        print("""
RTSLiveController (extends LiveDebugController)

Game Flow:
  ctrl.create_lobby(name, max_players=4)
  ctrl.add_ai_players(count, race="swarm")
  ctrl.select_race("tech")
  ctrl.start_match()
  ctrl.leave_match()

State & Debugging:
  state = ctrl.get_game_state_summary()
  ctrl.take_screenshot("before-fog-fix")

Powerful Recording (new):
  ctrl.start_tracing("my-test")
  ctrl.stop_tracing("trace.zip")
  ctrl.start_video_recording()
  ctrl.stop_video_recording()
  result = ctrl.record_full_game("my-full-match", duration_seconds=90)

  ctrl.help()
        """)


def main():
    print("RTS Game Live Debug Controller")
    print("Connecting to your running Neon Dominion client...\n")

    ctrl = RTSLiveController()
    ctrl.connect(target_url="http://localhost:5000")
    ctrl.help()

    print("Dropping into interactive REPL. Use 'ctrl'.")
    namespace = {"ctrl": ctrl, "help": ctrl.help}
    code.interact(local=namespace, banner="")
    ctrl.close()


if __name__ == "__main__":
    main()
