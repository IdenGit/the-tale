# coding: utf-8

from django.conf import settings as project_settings
from django.utils.log import getLogger

from game.text_generation import get_vocabulary, get_dictionary, prepair_substitution

logger = getLogger('the-tale.workers.game_logic')


class Writer(object):

    def __init__(self, type, message, substitution):
        self.type = type
        self.message = message
        self.substitution = prepair_substitution(substitution)

    def name_id(self): return 'quest_%s_name' % (self.type, )

    def action_id(self): return 'quest_%s_action_%s' % (self.type, self.message)

    def journal_id(self): return 'quest_%s_journal_%s' % (self.type, self.message)

    def diary_id(self): return 'quest_%s_diary_%s' % (self.type, self.message)

    def choice_variant_id(self, variant): return 'quest_%s_choice_%s_variant_%s' % (self.type, self.message, variant)

    def current_choice_id(self, answer): return 'quest_%s_choice_%s_current_%s' % (self.type, self.message, answer)

    def name(self):
        return self.get_message(self.name_id())

    def action(self, ):
        return self.get_message(self.action_id())

    def journal(self, **kwargs):
        return self.get_message(self.journal_id(), **kwargs)

    def diary(self, **kwargs):
        return self.get_message(self.diary_id(), **kwargs)

    def choice_variant(self, variant):
        return self.get_message(self.choice_variant_id(variant))

    def current_choice(self, answer):
        return self.get_message(self.current_choice_id(answer))


    def get_message(self, type_, **kwargs):

        vocabulary = get_vocabulary()

        if type_ not in vocabulary:
            if not project_settings.TESTS_RUNNING:
                logger.error('writer:get_message: unknown template type: %s', type_)
            return None

        template = vocabulary.get_random_phrase(type_, None)

        if template is None:
            # if template type exists but empty
            return None

        if kwargs:
            args = dict(self.substitution)
            args.update(prepair_substitution(kwargs))
        else:
            args = self.substitution

        return template.substitute(get_dictionary(), args)
