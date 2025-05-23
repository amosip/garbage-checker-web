class Config:
    def __init__(self):
        self.min_text_length = 100
        self.avg_line_length_threshold = 20
        self.char_entropy_threshold = 3.5
        self.non_alpha_ratio_threshold = 0.5
        self.long_word_threshold = 5

    def get_settings(self):
        return {
            "min_text_length": self.min_text_length,
            "avg_line_length_threshold": self.avg_line_length_threshold,
            "char_entropy_threshold": self.char_entropy_threshold,
            "non_alpha_ratio_threshold": self.non_alpha_ratio_threshold,
            "long_word_threshold": self.long_word_threshold,
        }