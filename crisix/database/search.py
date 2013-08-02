import re, operator
from django.db.models import Q
from substr import long_substr

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):
    '''
    Returns a query, that is a combination of Q objects. That combination
    aims to search keywords within a model by testing the given search fields.
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

def insertion_sort(sequence, value, *bf):
    for i in range(len(sequence)):
        if ((value < sequence[i]) if bf is () else bf[0](value, sequence[i])):
            return sequence.insert(i, value)
    sequence.append(value)

def relevance_sort(query_string, search_fields, query_set):
    sorted_set = []
    for entry in query_set:
        substr = [long_substr([getattr(entry, field).lower(), query_string.lower()]) for field in search_fields]
        match = float(max([len(s) for s in substr])) / len(query_string)
        insertion_sort(sorted_set, (match, entry), lambda x, y: x[0] > y[0])
    return zip(*sorted_set)[1]

def contextualize(summary, query_string):
    context = re.search('(^| )(' + query_string + ')($|[ ?.,!])', summary, re.IGNORECASE)
    if context is None:
        #fix
        return ' '.join(summary.split()[:50])
    else:
        pivot = context.group(0)
        head, tail = summary.split(pivot, 1)
        head = head.split()[-20:]
        tail = tail.split()[:30]
        context = ' '.join(head + [pivot] + tail).lstrip('.?!,0123456789 ').rstrip(',')
        return ('... ' if (context[0].islower() or context[0].isdigit()) else '') + (context if context.endswith('.') else context + ' ...')
