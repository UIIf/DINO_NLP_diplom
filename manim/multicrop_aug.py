from manim import *
import cv2
import numpy as np

config.background_color = WHITE
config.frame_rate = 60

def create_custom_bar_char(values, bar_colors, x_length, y_length, y_range):
        bars = VGroup()
        bar_width = x_length/len(values) * 0.8
        spacing =  x_length/len(values) * 0.2

        max_height = y_range[-1] - y_range[0]
        if y_range[0] * y_range[1]  <= 0:
            bars.add(NumberLine(length=x_length, stroke_width=5, tick_size=0).move_to(DOWN * y_length/2 + UP * -y_range[0]/max_height * y_length))
        bars.add(NumberLine(length=y_length).rotate(PI/2).set_opacity(0))
        for i, (v, color) in enumerate(zip(values, bar_colors)):
            bar = Rectangle(
                height=v/max_height * y_length,
                width=bar_width,
                fill_color=color,
                fill_opacity=0.8,
            )
            
            bar.move_to((i - len(values)/2 + 0.5) * (bar_width + spacing) * RIGHT + UP * (v/max_height * y_length/2 - y_length/2 - y_range[0]/max_height * y_length ))

            bars.add(bar)
        return bars

def create_embedding_bar(values:list[int], width=1, y_range=(-1, 1),color=random_bright_color(), high_value_color = BLUE_B, low_value_color=RED_B):
    left_border = Tex("[", color=color).scale(2)

    bc = create_custom_bar_char(
        values, 
        y_range=y_range,
        y_length=left_border.height,
        x_length=width,
        bar_colors= [high_value_color if c > 0 else low_value_color for c in values],
        # x_axis_config={"include_tip": False, "include_ticks": False,},
        # y_axis_config={
        #     "stroke_opacity": 0, 
        #     "include_numbers": False,
        #     "include_tip": False,
        #     "include_ticks": False,
        # }
        
    )
    # bc.y_axis.numbers.set_opacity(0)
    left_border.next_to(bc, LEFT, buff=0.1).scale_to_fit_height(bc.height*1.1)
    right_border = Tex("]", color=color).scale_to_fit_height(bc.height*1.1).next_to(bc, RIGHT, buff=0.1)
    return VGroup(left_border, bc, right_border)

def rotate_to_vertical_bc(bc, angle, anim=True):
    left, bc, right = bc
    if anim:
        bc.rotate(angle)
        return AnimationGroup(
            left.animate.scale_to_fit_height(bc.height*1.1).next_to(bc, LEFT),
            right.animate.scale_to_fit_height(bc.height*1.1).next_to(bc, RIGHT),
            bc.rotate(-angle).animate.rotate(angle),
        )
    else:
        bc.rotate(angle)
        left.scale_to_fit_height(bc.height*1.1).next_to(bc, LEFT)
        right.scale_to_fit_height(bc.height*1.1).next_to(bc, RIGHT)

class Main(Scene):

    def construct(self):
        VMobject.set_default(stroke_color=BLACK)

        image_np = cv2.imread("dog.jpeg")[...,::-1]
        image = ImageMobject(image_np).set_opacity(0)

        global_crop_np = image_np[:int(image_np.shape[0]*3/4), int(image_np.shape[1]/4):]
        global_crop = ImageMobject(global_crop_np).set_opacity(0)
        global_crop_border = Rectangle(BLUE, global_crop.height, global_crop.width)
        global_crop_group = Group(global_crop, global_crop_border).move_to((3/4, 3/4, 0))
        global_caption = always_redraw(lambda : Tex("Global crop").set_opacity(global_crop.fill_opacity).next_to(global_crop, DOWN, buff=0.2))

        local_crop_np = image_np[int(image_np.shape[0] *3/ 4):, :int(image_np.shape[1]/4)]
        local_crop = ImageMobject(local_crop_np).set_opacity(0)
        local_crop_border = Rectangle(RED, local_crop.height, local_crop.width)
        local_crop_group = Group(local_crop, local_crop_border).move_to((-9/4, -8.8/4, 0))
        local_caption = always_redraw(lambda : Tex("Local crop").set_opacity(local_crop.fill_opacity).next_to(local_crop, DOWN, buff=0.2))
        
        # self.add(image, global_crop, local_crop)
        image_cption = always_redraw(lambda : Tex("Original image").set_opacity(image.fill_opacity).next_to(image, DOWN, buff=0.2))
        
        self.play(image.animate.set_opacity(1), Create(image_cption))
        self.wait(1)
        self.play(
            image.animate.set_opacity(0.1),
        )
        self.play(Create(global_crop_border), Create(global_caption), global_crop.animate.set_opacity(1), run_time=1)
        self.wait(1)
        self.play(Create(local_crop_border), Create(local_caption), local_crop.animate.set_opacity(1), run_time=1)
        self.wait(1)
        self.play(
            AnimationGroup(
                image.animate.shift(LEFT*3).set_opacity(1),
                global_crop_group.animate.shift(RIGHT * 3).shift(UP * 1).scale(0.8),
                local_crop_group.animate.shift(RIGHT * 6).scale(1.5).shift(UP*0.1)
            )
        )
        self.wait(1)

        self.play(
            image.animate.set_opacity(0),
            global_crop_group.animate.shift(LEFT * 7).shift(DOWN * 1.2).scale(1.4),
            local_crop_group.animate.shift(UP * 2.7).scale(2.2),
        )

        self.remove(image, image_cption)

        # Embeddings
        global_embed_bc = create_embedding_bar([0.2, 0.4, -0.8, 0.3, -0.5, 0.2], global_crop.width * 0.8, color=BLUE).next_to(global_caption, DOWN, buff=0.1)
        global_arrow = Line(global_crop.get_bottom(), end=global_embed_bc.get_top(), buff=0.2, color=BLUE).add_tip()


        local_embed_bc = create_embedding_bar([0.3, -0.2, -0.5, 0.8, -0.2, 0.4], global_crop.width * 0.8, color=RED).next_to(local_caption, DOWN, buff=0.1)
        local_arrow = Line(local_crop.get_bottom(), end=local_embed_bc.get_top(), buff=0.2, color=RED).add_tip()

        # Captions to embeddingss
        self.play(Transform(global_caption, VGroup(global_embed_bc, global_arrow)), Transform(local_caption, VGroup(local_embed_bc, local_arrow)))
        self.add(global_embed_bc, global_arrow, local_embed_bc, local_arrow)
        self.remove(global_caption, local_caption)
        self.wait(1)

        # Remove image, add vertical embeddings
        self.play(
            FadeOut(local_crop, local_arrow, local_crop_border, global_crop, global_arrow, global_crop_border),
            global_embed_bc.animate.move_to(LEFT * 3),
            local_embed_bc.animate.move_to(RIGHT * 3),
        )
        self.wait(1)
        self.play(
            rotate_to_vertical_bc(global_embed_bc, -PI/2), 
            rotate_to_vertical_bc(local_embed_bc,  -PI/2),
        )



        # Only global crop
        self.play(
             global_embed_bc.animate.move_to(0).shift(DOWN),
             FadeOut(local_embed_bc),
        )
        self.wait(1)

        # Other global embeddings
        other_global_emb_values = [
            [0.3, 0.6, -0.7, 0.6, -0.4, 0.1],
            [0.1, 0.5, -0.7, 0.4, -0.3, 0.1],
            [0.4, 0.5, -0.9, 0.2, -0.2, 0.1],
            [0.3, 0.3, -0.6, 0.5, -0.6, 0.3],
        ]

        other_embeds = [create_embedding_bar(v, global_crop.width * 0.8, color=BLUE) for v in other_global_emb_values]

        for i in range(len(other_embeds)):
            x = i//2 * 2 - 1
            y = i%2 * 2 - 1
            rotate_to_vertical_bc(other_embeds[i].shift(UP*y *1.5 + RIGHT*x * 4).scale(0.5), -PI/2, anim=False)

        other_predictions_caption = Tex("Other teacher predictions").shift(UP*2)
        self.play(FadeIn(*other_embeds), Create(other_predictions_caption))
        self.wait(1)

        # Other global embeddings to sum
        other_embeds_animation = AnimationGroup(*[other_embeds[i].animate.move_to(RIGHT * 3).shift(RIGHT * i*0.2).set_opacity((4 - i)/4) for i in range(len(other_embeds))])
        fc = other_embeds[0].get_center()
        other_embeds[0].move_to(RIGHT*3)
        sigma = Tex("$$\\frac{1}{n}\\Sigma$$", color=BLUE).scale_to_fit_height(other_embeds[0].height).next_to(other_embeds[0], LEFT, buff=0.2)
        other_embeds[0].move_to(fc)

        self.play(
            Uncreate(other_predictions_caption),
            other_embeds_animation,
            Create(sigma),
            global_embed_bc.animate.move_to(LEFT * 3),
        )

        self.wait(1)

        # Group to centering vector
        centering = create_embedding_bar([0.275, 0.475, -0.725, 0.425, -0.375, 0.15], global_crop.width * 0.8, color=YELLOW).move_to(RIGHT * 3)
        rotate_to_vertical_bc(centering, -PI/2, anim=False)
        self.play(Transform(VGroup(*other_embeds, sigma), centering))
        self.remove(*other_embeds, sigma)
        self.add(centering)
        self.wait(1)

        # Subtraction
        minus = Tex("-").scale_to_fit_width(global_embed_bc.width/3)
        self.play(Create(minus))
        self.wait(1)


        new_global_enbed_bc = create_embedding_bar([-0.1, 0, -0.1, -0.2, -0.2, 0.1], global_crop.width * 0.8, color=BLUE)
        rotate_to_vertical_bc(new_global_enbed_bc, -PI/2, anim=False)
        self.remove(centering)

        self.play(Transform(VGroup(global_embed_bc, minus, centering), new_global_enbed_bc))
        self.remove(global_embed_bc, minus, centering)
        self.add(new_global_enbed_bc)
        self.wait(1)

        # Sharpening

        sharpening_tex = Tex(r"$$P(x)^{(i)} = \frac{\displaystyle exp\Bigg(\frac{g_\theta(x)^{(i)}}{\tau}\Bigg)}{\displaystyle \sum^K_{k=1}exp\Bigg(\frac{g_\theta(x)^{(k)}}{\tau}\Bigg)}$$").move_to(RIGHT*2)
        self.play(new_global_enbed_bc.animate.move_to(LEFT * 3.5), Create(sharpening_tex))
        self.wait(3)

        # P(new_embed_bc)
        temp_left, temp_bc, temp_right = new_global_enbed_bc
        temp_bc_center = temp_bc.get_center()
        temp_bc.move_to(0).rotate(PI/2).scale(2)
        animations = AnimationGroup(
            temp_left.animate.scale_to_fit_height(temp_bc.height*1.1).next_to(temp_bc, LEFT),
            temp_right.animate.scale_to_fit_height(temp_bc.height*1.1).next_to(temp_bc, RIGHT)
        )
        left_p = Tex("P(").scale_to_fit_height(temp_bc.height*1.1).next_to(temp_bc, LEFT, buff=0.7)
        right_p = Tex(")").scale_to_fit_height(temp_bc.height*1.1).next_to(temp_bc, RIGHT, buff=0.7)
        temp_bc.move_to(temp_bc_center).rotate(-PI/2).scale(0.5)

        self.play(animations, temp_bc.animate.move_to(0).rotate(PI/2).scale(2), Transform(sharpening_tex, VGroup(left_p, right_p)))
        self.remove(sharpening_tex)
        self.add(left_p, right_p)
        self.wait(1)

        x = Tex("X").move_to(LEFT*5)
        right_p_2 = Tex(") =").scale_to_fit_height(x.height * 2).next_to(x, RIGHT, buff=0.1)
        
        tau = ValueTracker(1)
        embeddings =np.array([-0.1, 0, -0.1, -0.2, -0.2, 0.1])
        sharpened_embedding = always_redraw(lambda : create_embedding_bar(np.exp(embeddings/tau.get_value())/np.exp(embeddings/tau.get_value()).sum(), global_crop.width * 0.8, color=BLUE, y_range=(0, 1)).scale(2).shift(RIGHT))
        tau_tex = always_redraw(lambda : Tex(f'$\\tau = {tau.get_value():.1f}$').move_to(DOWN*3))
        self.play(
            left_p.animate.scale_to_fit_height(x.height * 2).next_to(x, LEFT, buff=0.1),
            Transform(right_p, right_p_2),
            FadeIn(sharpened_embedding),
            Transform(new_global_enbed_bc, x),
            Create(tau_tex),
        )
        self.remove(new_global_enbed_bc, right_p)
        self.add(x, right_p_2)
        self.wait(1)

        # Sharpening demonstrations
        self.play(tau.animate.set_value(0.1))
        self.wait(1)
        



