import wikipedia


answer_results = {}


answer = 'blue jay'
records = wikipedia.search(answer)
# print records
r = records[0] if len(records) else None
print r

if r is not None:
    p = wikipedia.page(r)

    answer_results[answer] = {
        "content": p.content,
        # "words": p.content.split(" ")
    }
print answer_results    