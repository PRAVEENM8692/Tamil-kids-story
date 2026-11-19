"""Manim animations for the crime videos (Tamil labels, dark background, 1280x720).
Render: manim -qh -r 1280,720 --fps 30 crime/manim_scenes.py SceneName   (the crime-manim workflow does this)
Each scene is a full-frame clip that build.py lays over the pictures for its length (plan.json "animations")."""
import random
from manim import *

TA = "Noto Sans Tamil"
BG, WHITE, YEL, RED, GRN, GREY = "#0d0d10", "#f5f5f5", "#ffd633", "#e5333b", "#3fcf7a", "#8a8f98"
config.background_color = BG

def T(s, size=34, color=WHITE, weight=BOLD):
    return Text(s, font=TA, font_size=size, color=color, weight=weight)

def title(s):
    t = T(s, 44, YEL); t.to_edge(UP, buff=0.45); u = Line(LEFT * 3.2, RIGHT * 3.2, color=RED, stroke_width=5).next_to(t, DOWN, buff=0.15); return VGroup(t, u)

class SenjiTimeline1(Scene):       # part 1: from the birthday to the CB-CID transfer (about 14 s)
    def construct(self):
        ttl = title("காலவரிசை"); self.play(Write(ttl), run_time=1.0)
        line = Line(LEFT * 5.6, RIGHT * 5.6, color=GREY, stroke_width=4).shift(DOWN * 0.2); self.play(Create(line), run_time=1.0)
        pts = [("அக் 11", "பிறந்தநாள்", -4.6, YEL), ("அக் 12", "அதிகாலை 3 மணி\nமாயம்", -1.6, RED), ("அக் 22", "வழக்கு\nசிபிசிஐடிக்கு", 1.6, GRN), ("அக் 23", "சிபிசிஐடி\nவரைபடம், விசாரணை", 4.6, WHITE)]
        for d, lab, x, c in pts:
            dot = Dot(RIGHT * x + DOWN * 0.2, radius=0.16, color=c); a = T(d, 30, c).next_to(dot, UP, buff=0.35); b = T(lab, 24, WHITE, NORMAL).next_to(dot, DOWN, buff=0.35)
            self.play(GrowFromCenter(dot), FadeIn(a, shift=DOWN * 0.2), FadeIn(b, shift=UP * 0.2), run_time=1.3)
        note = T("இன்னும் குழந்தை கிடைக்கவில்லை · கைது இல்லை", 30, RED).to_edge(DOWN, buff=0.7); self.play(FadeIn(note), run_time=1.0); self.wait(3.2)

class SenjiTowerDump(Scene):       # part 2: the mobile tower data, 600+ numbers narrowed down (about 13 s)
    def construct(self):
        ttl = title("டவர் டம்ப்"); self.play(Write(ttl), run_time=1.0)
        random.seed(7); towers = [LEFT * 4.2, ORIGIN, RIGHT * 4.2]; ring = VGroup(); dots = VGroup()
        for k, c in enumerate(towers):
            tw = VGroup(Triangle(color=YEL, fill_opacity=1, stroke_width=0).scale(0.22), Circle(radius=1.35, color=YEL, stroke_width=2, stroke_opacity=0.5)).move_to(c + DOWN * 0.3); ring.add(tw)
            for _ in range(38):
                ang, r = random.random() * TAU, 1.2 * random.random() ** 0.5
                dots.add(Dot(c + DOWN * 0.3 + np.array([r * np.cos(ang), r * np.sin(ang), 0]), radius=0.05, color=GREY))
        self.play(FadeIn(ring), run_time=0.8)
        tr = ValueTracker(0); cnt = always_redraw(lambda: T(f"{int(tr.get_value())}+ செல்போன் எண்கள்", 36, WHITE).to_edge(DOWN, buff=0.7))
        self.add(cnt); self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.02), tr.animate.set_value(600), run_time=4.0)
        keep = VGroup(*random.sample(list(dots), 6)); rest = VGroup(*[d for d in dots if d not in keep])
        self.play(rest.animate.set_opacity(0.08), keep.animate.set_color(RED).scale(2.2), run_time=2.0)
        lab = T("சந்தேகத்துக்குரிய எண்கள் மட்டும் கண்காணிப்பு", 32, RED).next_to(cnt, UP, buff=0.35); self.play(FadeIn(lab), run_time=1.0); self.wait(3.0)

class SenjiFoundNot(Scene):        # part 2: what has and has not been found (about 14 s)
    def construct(self):
        ttl = title("இதுவரை"); self.play(Write(ttl), run_time=1.0)
        L = [("600 போன் எண்கள் ஆய்வு", GRN), ("3 டவர் தரவு", GRN), ("சிசிடிவி காட்சிகள்", GRN), ("தடயவியல் மாதிரிகள்", GRN)]
        R = [("சிறுமி", RED), ("உறுதியான சாட்சி", RED), ("பணம் கேட்ட போன்", RED), ("கைது", RED)]
        hl = T("கிடைத்தது", 34, GRN).move_to(LEFT * 3.3 + UP * 1.5); hr = T("கிடைக்கவில்லை", 34, RED).move_to(RIGHT * 3.3 + UP * 1.5); self.play(FadeIn(hl), FadeIn(hr), run_time=0.8)
        for k in range(4):
            a = VGroup(T("✔", 30, GRN), T(L[k][0], 28, WHITE, NORMAL)).arrange(RIGHT, buff=0.25).move_to(LEFT * 3.3 + UP * (0.6 - 0.9 * k))
            b = VGroup(T("✖", 30, RED), T(R[k][0], 28, WHITE, NORMAL)).arrange(RIGHT, buff=0.25).move_to(RIGHT * 3.3 + UP * (0.6 - 0.9 * k))
            self.play(FadeIn(a, shift=RIGHT * 0.3), FadeIn(b, shift=LEFT * 0.3), run_time=1.1)
        self.wait(3.5)
