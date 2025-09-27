import logging
import queue
import threading
import time
import typing
import random
from dataclasses import dataclass

import library
from matrix_button_led_controller import MatrixButtonLEDController

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
USE_LED_HAT = True

@dataclass
class ButtonInfo:
    color: str
    sound: str
    matched: bool


class Game:
    def __init__(self, button_pad: MatrixButtonLEDController):
        self.button_pad = button_pad
        self.button_pad.assign_button_events(self.when_pressed, self.when_held, self.when_released)
        self.buttons: typing.List[ButtonInfo] = []
        self.sounds: typing.List[str] = []
        self.colors: typing.List[str] = []
        self.randomColor: typing.List[str] = []
        self.randomSounds: typing.List[str] = []
        self.speaker = library.speaker.Speaker()
        self.initialize_button_pad()
        self.started = False
        self.play_game = True
        self.queue = queue.Queue()
        self.startTime = 0
        self.endTime = 0
        self.holding = False
        self.buttonHeld = 0
        self.memoryMode = False
        self.buttonFlipFlop = True
        self.button1 = None
        self.button2 = None
        self.buttonColor = "black"
        self.in_game_sounds: typing.List[str] =[]
        self.pairs = 0

    @property
    def correct_sound(self):
        self.speaker.play_preloaded_wav("thunder2", wait_until_done = True)
        return "correct_answer"

    @property
    def incorrect_sound(self):
        """The sound that is played when player makes an incorrect guess"""
        self.speaker.play_preloaded_wav("fart_z", wait_until_done = True)
        # OPTIONAL: change this to a different sound if you want
        return "incorrect"

    @property
    def end_of_game_sound(self):
        """The sound that is played when the game ends."""
        # OPTIONAL: change this to a different sound if you want
        self.speaker.play_preloaded_wav("end_of_game", wait_until_done = True)
        return "end_of_game"

    def _background_logic_checker(self):
        while self.play_game:
            # time.sleep(0.005)  # Prevents busy-waiting
            if self.queue.empty():
                continue
        
            button_number = self.queue.get()
            button_color = self.randomColor[button_number-1]

            
            # print(f"Handling button {button_number} " + "Color" + self.randomColor[button_pressed1-1])
            # button_pressed2 = self.queue.get()
            # print(self.randomColor[button_pressed2])
            # print(button_pressed2)



            # Example logic: light up the button that was pressed with a constant color
            button = self.button_pad.get_button(button_number)
            self.button_pad.set_button_led_color(button, self.randomColor[button.pin.info.number-1])
            self.speaker.play_preloaded_wav(self.randomSounds[button_number-1], wait_until_done=True)  # Play a sound when button is pressed
            # TODO: check your game state, and update things

            if self.button2 != None and self.button1 != None and self.buttonFlipFlop:
                if self.randomColor[self.button1-1] == self.randomColor[self.button2-1]:
                    print("right")
                    self.speaker.play_preloaded_wav("correct_answer", wait_until_done = True)
                    self.pairs += 1
                else:
                    print("wrong")
                    self.speaker.play_preloaded_wav("incorrect", wait_until_done = True)
                    self.buttonColor = "black"
                    self.button_pad.set_button_led_color(self.button_pad.get_button(self.button1), self.buttonColor)
                    time.sleep(1)
                    self.button_pad.set_button_led_color(self.button_pad.get_button(self.button2), "black")
                    # time.sleep(1)
                    self.button1 = None
                    self.button2 = None
                    if(self.memoryMode):
                        for x in range(len(self.randomColor)):
                            self.button_pad.set_button_led_color(self.button_pad.get_button(x+1), "red")
            if(self.pairs >= 8):
                for x in range(len(self.randomColor)):
                    self.button_pad.set_button_led_color(self.button_pad.get_button(x+1), "green") 
                    self.speaker.play_preloaded_wav("gasp_x", wait_until_done = True)




    def when_pressed(self, button):
        # TODO: this is called when a button is pressed. Add what you need to here
        _logger.info(f"Button {button.pin.info.number} pressed")
        self.queue.put(button.pin.info.number)
        if(self.buttonFlipFlop):
            self.button1 = button.pin.info.number
            print("button1: " + str(self.button1))
            self.buttonFlipFlop = False
        else:
            self.button2 = button.pin.info.number
            print("Button 2: " + str(self.button2))
            self.buttonFlipFlop = True




    def when_held(self, button):
        # TODO: this is called when a button is held. Add what you need to here
        print("holding")
        self.holding = True
        self.buttonHeld = button.pin.info.number
        

    def when_released(self, button):
        if(self.holding):
            print("resetting")
            if(self.buttonHeld == 1):
                print("button 1 held")
                self.initialize_button_pad()
                self.buttonFlipFlop = True
                self.button1 = None
                self.speaker.play_preloaded_wav("end_of_game", wait_until_done = True)
            elif(self.buttonHeld == 2):
                print("button 2 held")
                for x in range(len(self.randomColor)):
                    self.button_pad.set_button_led_color(self.button_pad.get_button(x+1), self.randomColor[x])
            elif(self.buttonHeld == 3):
                print("button 3 held")
                for x in range(len(self.randomColor)):
                    self.button_pad.set_button_led_color(self.button_pad.get_button(x+1), self.randomColor[x])   
                time.sleep(5)
                self.memoryMode = True
                self.buttonFlipFlop = True
                self.button1 = None
                self.button_pad.clear_button_pad()
                

        self.holding = False 
        



    def initialize_button_pad(self):
        self.pairs = 0
        self.memoryMode = False
        self.button_pad.clear_button_pad()
        self.randomColor = []
        self.randomSounds = []
        # TODO: Set all buttons to a color, List of colors to choose from: https://github.com/waveform80/colorzero/blob/master/colorzero/tables.py#L315
        # sounds are available in the sounds directory
        self.in_game_sounds = [
            "drum_roll2",
            "end_of_game"
        ]

        self.sounds = [
            "thunder2",
            "fart_z",
            "baby_x",
            "slide_whistle_x",
            "arrow2",
            "phone_pay",
            "bloop_x",
            "car_horn_x",
            "thunder2",
            "fart_z",
            "baby_x",
            "slide_whistle_x",
            "arrow2",
            "phone_pay",
            "bloop_x",
            "car_horn_x",
        ]

        
        self.colors = [
            "red",
            "blue",
            "green",
            "yellow",
            "purple",
            "deeppink",
            "white",
            "cyan",
            "red",
            "blue",
            "green",
            "yellow",
            "purple",
            "deeppink",
            "white",
            "cyan"
        ]
        # TODO: assign to buttons

        num = 0

        for x in range(16):
            num = random.randrange(len(self.colors))
            self.randomColor.append(self.colors.pop(num))
            self.randomSounds.append(self.sounds.pop(num))
            


    def _start_game(self):
        self.thread = threading.Thread(target=self._background_logic_checker)
        self.thread.start()
        # TODO: play a sound to start the game
        self.speaker.play_preloaded_wav("drum_roll2", wait_until_done = True)
        self.started = True

    def play(self):
        self._start_game()
        try:
            input("Press Enter to exit the game...")
        except KeyboardInterrupt:
            print("Exiting game...")
        finally:
            self.play_game = False
            self.thread.join()
            self.button_pad.cleanup()


def _main():
    button_pad = MatrixButtonLEDController(
        scan_delay=0.020, pwm_freq=10000, display_pause=0.001, use_led_hat=USE_LED_HAT
    )
    game = Game(button_pad)
    game.play()


if __name__ == "__main__":
    _main()