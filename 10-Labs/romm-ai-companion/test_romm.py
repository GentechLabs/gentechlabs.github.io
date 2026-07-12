"""
Tests for RomM AI Companion modules.
"""
import sys, os, json, time, unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(__file__))

from screen_capture import CapturePipeline, CaptureConfig, SimulatedCapturer, FrameBuffer, GameFrame
from vision_analysis import VisionAnalyzer, StateTracker, GameState, GameGenre
from decision_engine import DecisionEngine, PlayStyle, Decision
from input_emulation import InputController, SimulatedEmitter, GameButton, InputSequence, Macros
from ai_companion import AICompanion, AgentConfig


class TestScreenCapture(unittest.TestCase):
    def test_simulated_capture(self):
        capturer = SimulatedCapturer()
        frame = capturer.capture()
        self.assertIsNotNone(frame)
        self.assertEqual(frame.source, "simulated")
        self.assertGreater(len(frame.image_data), 0)

    def test_frame_buffer(self):
        buf = FrameBuffer(max_frames=5)
        for i in range(10):
            buf.add(GameFrame(
                timestamp=time.time(), frame_id=f"f{i:04d}",
                width=256, height=240, image_data=b"test", game="test", source="simulated"
            ))
        self.assertEqual(buf.size, 5)
        self.assertEqual(buf.count, 10)

    def test_capture_pipeline(self):
        pipeline = CapturePipeline()
        frame = pipeline.capture_frame()
        self.assertIsNotNone(frame)
        self.assertEqual(pipeline.buffer.size, 1)

    def test_capture_burst(self):
        pipeline = CapturePipeline()
        frames = pipeline.capture_burst(3, 0.01)
        self.assertEqual(len(frames), 3)


class TestVisionAnalysis(unittest.TestCase):
    def test_simulated_analysis(self):
        analyzer = VisionAnalyzer()
        state = analyzer._simulate_analysis("test_001")
        self.assertIsNotNone(state.health)
        self.assertIsNotNone(state.score)
        self.assertIn(state.genre, list(GameGenre))

    def test_state_tracker(self):
        tracker = StateTracker(window=5)
        for i in range(10):
            tracker.update(GameState(
                frame_id=f"f{i:04d}", timestamp=time.time(),
                health=0.5, score=100, lives=3,
            ))
        self.assertEqual(len(tracker._states), 5)

    def test_health_trend(self):
        tracker = StateTracker()
        for h in [1.0, 0.8, 0.6, 0.4, 0.2]:
            tracker.update(GameState(
                frame_id="f", timestamp=time.time(), health=h, score=0, lives=3,
            ))
        self.assertEqual(tracker.health_trend(), "declining")

    def test_in_danger(self):
        tracker = StateTracker()
        for h in [0.5, 0.4, 0.3, 0.2, 0.1]:
            tracker.update(GameState(
                frame_id="f", timestamp=time.time(), health=h, score=0, lives=3,
            ))
        self.assertTrue(tracker.is_in_danger())

    def test_summary(self):
        tracker = StateTracker()
        tracker.update(GameState(
            frame_id="f", timestamp=time.time(), game="test",
            health=0.8, score=500, lives=3, level="1-1",
        ))
        s = tracker.summary()
        self.assertEqual(s["status"], "active")
        self.assertEqual(s["game"], "test")


class TestInputEmulation(unittest.TestCase):
    def test_simulated_emitter(self):
        emitter = SimulatedEmitter()
        emitter.press(GameButton.A)
        emitter.release(GameButton.A)
        self.assertEqual(len(emitter.history), 2)

    def test_input_sequence(self):
        seq = InputSequence(name="test")
        seq.add(GameButton.RIGHT, 0.1)
        seq.add(GameButton.A, 0.1)
        self.assertEqual(len(seq.actions), 4)  # 2 press + 2 release

    def test_macros(self):
        m = Macros()
        self.assertEqual(m.jump().name, "jump")
        self.assertEqual(m.attack().name, "attack")
        self.assertGreater(m.dash_right().total_duration, 0)

    def test_controller(self):
        controller = InputController(SimulatedEmitter())
        controller.jump()
        controller.attack()
        controller.move("right", 0.1)
        self.assertGreater(len(controller.emitter.history), 0)


class TestDecisionEngine(unittest.TestCase):
    def test_aggressive_style(self):
        engine = DecisionEngine(PlayStyle.AGGRESSIVE)
        state = GameState(frame_id="f", timestamp=time.time(), enemies_visible=3)
        tracker = StateTracker()
        tracker.update(state)
        d = engine.decide(state, tracker)
        self.assertEqual(d.action, "attack")

    def test_defensive_style(self):
        engine = DecisionEngine(PlayStyle.DEFENSIVE)
        state = GameState(frame_id="f", timestamp=time.time(), enemies_visible=3)
        tracker = StateTracker()
        tracker.update(state)
        d = engine.decide(state, tracker)
        self.assertEqual(d.action, "dodge")

    def test_game_over(self):
        engine = DecisionEngine()
        state = GameState(frame_id="f", timestamp=time.time(), is_game_over=True)
        tracker = StateTracker()
        tracker.update(state)
        d = engine.decide(state, tracker)
        self.assertEqual(d.action, "wait")

    def test_danger_priority(self):
        engine = DecisionEngine()
        tracker = StateTracker()
        for h in [0.5, 0.3, 0.2, 0.1]:
            tracker.update(GameState(
                frame_id="f", timestamp=time.time(), health=h, score=0, lives=1,
            ))
        state = tracker.latest()
        d = engine.decide(state, tracker)
        self.assertEqual(d.priority, 10)


class TestAICompanion(unittest.TestCase):
    def test_agent_creation(self):
        agent = AICompanion(AgentConfig(max_loops=5, verbose=False))
        self.assertIsNotNone(agent.capture)
        self.assertIsNotNone(agent.vision)
        self.assertIsNotNone(agent.decision)
        self.assertIsNotNone(agent.input)

    def test_agent_run(self):
        agent = AICompanion(AgentConfig(max_loops=5, verbose=False))
        agent.start()
        self.assertGreater(agent.loops, 0)
        self.assertGreater(agent.frames_processed, 0)
        self.assertGreater(agent.decisions_made, 0)

    def test_agent_summary(self):
        agent = AICompanion(AgentConfig(max_loops=3, verbose=False))
        agent.start()
        s = agent.summary()
        self.assertEqual(s["status"], "stopped")
        self.assertIn("loops", s)
        self.assertIn("frames", s)


if __name__ == "__main__":
    unittest.main()
