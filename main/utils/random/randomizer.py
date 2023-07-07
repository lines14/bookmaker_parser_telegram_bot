import random

class Randomizer:
    @staticmethod
    def get_random_element(*all_elements_lists):
        base_elements_list = all_elements_lists[0][0]
        exceptions_list = all_elements_lists[0][1]
        while True:
            element = base_elements_list[random.randint(0, len(base_elements_list) - 1)]
            if element.id not in list(map(lambda element: element.id, exceptions_list)):
                return element.id

    @classmethod
    def get_random_string(cls, has_upper_case=False, has_number=False, has_cyrillic=False, chosen_letter=False, min_length=1, max_length=10):
        upper_case_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        lower_case_letters = 'abcdefghijklmnopqrstuvwxyz'
        numbers = '0123456789'
        cyrillic_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
      
        length = random.randint(min_length, max_length)
      
        random_string = ''
        if chosen_letter:
            random_string += chosen_letter
      
        required_characters = ''
        if has_upper_case:
            required_characters += upper_case_letters[random.randint(0, len(upper_case_letters) - 1)]
        if has_number:
            required_characters += numbers[random.randint(0, len(numbers) - 1)]
        if has_cyrillic:
            required_characters += cyrillic_letters[random.randint(0, len(cyrillic_letters) - 1)]

        random_string += required_characters
      
        characters = ''
        characters += lower_case_letters
        if has_upper_case:
            characters += upper_case_letters
        if has_number:
            characters += numbers
        if has_cyrillic:
            characters += cyrillic_letters

        random_length = length - len(random_string)
        counter = 0
        while counter < random_length:
            random_string += characters[random.randint(0, len(characters) - 1)]
            counter += 1

        return cls.string_shuffler(random_string)

    @staticmethod
    def string_shuffler(input_string):
        array = list(input_string)
        current_index = len(array) - 1
        while 0 != current_index:
            random_index = random.randint(0, current_index)
            current_index -= 1
            temporary_value = array[current_index]
            array[current_index] = array[random_index]
            array[random_index] = temporary_value
        
        return ''.join(array)