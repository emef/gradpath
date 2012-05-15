from pprint import pprint

from gradpath.courses.models import Course, Section
from gradpath.degrees.evaluation.classes import Container, Repeatable, Match
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

EVAL_COMPOUND_FORMAT="""\
<div class='eval-compound'>
    <div>
        {0}
    </div>
    <div>
        {1}
    </div>
</div>
"""

EVAL_SINGLE_FORMAT="""\
<div>
    {0}
</div>
"""

@register.filter
def degree_doc(evaluator):
    def gen_html(doc):
        if doc['children']:
            return EVAL_COMPOUND_FORMAT.format(
                doc['text'],
                '\n'.join(gen_html(child) for child in doc['children'])
            )
        else:
            return EVAL_SINGLE_FORMAT.format(doc['text'])
    
    doc = evaluator.doc('Requirements remaining:')
    return mark_safe(gen_html(doc))
    
