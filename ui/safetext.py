def safetext(text, safe=True):
    chars = {'~': 'tilde',
             '`': 'akut',
             '@': 'at',
             '#': 'sharp',
             '$': 'dollar',
             '%': 'percent',
             '^': 'circumflex',
             '&': 'ampersand',
             '*': 'star',
             '(': 'open parenthesis',
             ')': 'close parenthesis',
             '[': 'open bracket',
             ']': 'close bracket',
             '{': 'open brace',
             '}': 'close brace',
             '>': 'more',
             '<': 'less',
             '\\': 'backslash',
             '/': 'slash',
             '|': 'pipe',
             '"': 'quote',
             ':': 'colon',
             "'": 'apostrophe',
             '_': 'underscore'
             }
    salt = 'sometexttoaddtospecialcharacters'
    if safe:
        for key in chars.keys():
            text = text.replace(key, salt+chars[key]+salt)
    else:
        for key in chars.keys():
            text = text.replace(salt+chars[key]+salt, key)
    return text