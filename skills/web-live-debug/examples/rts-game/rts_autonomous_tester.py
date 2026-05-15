#!/usr/bin/env python3
"""
Autonomous RTS Game Tester (Reference Implementation)

This tester can play complete games of the Neon Dominion RTS autonomously
while you watch in the live browser. It was the primary tool used to
hunt down and fix deep bugs during development.

Usage:
    python -m examples.rts_game.rts_autonomous_tester --cycles 2

With full recording:
    python -m examples.rts_game.rts_autonomous_tester --cycles 1 --record
"""

import argparse
import time

from examples.rts_game.rts_controller import RTSLiveController
from testers.autonomous_web_tester import AutonomousWebTester


class RTSAutonomousTester(AutonomousWebTester):
    """Autonomous tester specialized for full RTS matches.

    Supports optional full tracing + video recording per cycle.
    """

    def __init__(self, record: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.record = record
        # Replace the generic controller with the RTS one
        self.controller = RTSLiveController(
            fresh_context=record,
            record_video=record,
            video_dir="recordings/rts-autonomous",
        )

    def run_test_cycle(self):
        ctrl: RTSLiveController = self.controller  # type: ignore

        trace_name = f"autonomous-{int(time.time())}"

        if self.record:
            ctrl.start_tracing(trace_name, screenshots=True, snapshots=True)
            print("[RTSTester] Tracing enabled for this cycle")

        # 1. Create a lobby
        ctrl.create_lobby("Autonomous Test " + str(int(time.time())), max_players=4)

        # 2. Fill with AI
        ctrl.add_ai_players(3, race="swarm")

        # 3. Pick a race and start
        ctrl.select_race("tech")
        ctrl.start_match()

        # 4. Let the game run for a while (watch the AI play)
        print("[RTSTester] Letting match run for 45 seconds of real time...")
        for i in range(9):
            time.sleep(5)
            state = ctrl.get_game_state_summary()
            print(f"  Tick ~{state.get('tick', 0)} | Units: {state.get('visibleUnits', 0)} | Zoom: {state.get('cameraZoom', 1):.2f}")

            if i % 3 == 0:
                ctrl.take_screenshot(f"game-{i}")

        # 5. Leave the match cleanly
        ctrl.leave_match()

        if self.record:
            trace_path = ctrl.stop_tracing()
            video_path = ctrl.stop_video_recording()
            print(f"[RTSTester] Recording saved: trace={trace_path}, video={video_path}")

        print("[RTSTester] Match cycle complete. Returned to lobby.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--continuous", action="store_true")
    parser.add_argument("--record", action="store_true", help="Enable tracing + video recording")
    args = parser.parse_args()

    tester = RTSAutonomousTester(record=args.record)
    tester.run(cycles=args.cycles, continuous=args.continuous)
