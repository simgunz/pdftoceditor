import re
import sys

BM_TEMPLATE = '''BookmarkBegin
BookmarkTitle: {title}
BookmarkLevel: {level:g}
BookmarkPageNumber: {page}'''

def get_toc_from_metadata(filename):
    toc = list()
    with open(filename) as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            if lines[i] == 'BookmarkBegin\n':
                title = lines[i+1][14:].strip('\n').strip(' ')
                level = lines[i+2][14:].strip('\n').strip(' ')
                page = lines[i+3][19:].strip('\n').strip(' ')
                toc.append((title, level, page))
                i+= 4
            else:
                i+=1

        toc = sorted(toc, key=lambda t: t[2])
    return toc

def add_toc_to_metadata(filename, toc, replace=True):
    with open(filename) as f:
        lines =[l for l in f.readlines() if not re.match('Bookmark.*', l)]
        for t in toc:
            bm = BM_TEMPLATE.format(title=t[0], level=t[1], page=t[2])
            lines.append(bm + '\n')
    with open(filename, 'w') as f:
        f.write("".join(lines))

def dump_toc(toc):
    for t in toc:
        print('{0} {1}{2}'.format(t[2],'  '*(int(t[1])-1),t[0]))

def load_toc(filename):
    toc = list()
    with open(filename) as f:
        for l in f:
            m = re.search('(\d+) ( *)(.*)', l)
            if m:
                title = m.group(3)
                level = (len(m.group(2))/2)+1
                page = m.group(1)
                toc.append((title, level, page))
    return toc

if __name__ == "__main__":
    #toc = get_toc("Analisi dei dati.txt")
    #dump_toc(toc)
    toc = load_toc(sys.argv[1])
    add_toc_to_metadata('metadata.txt', toc)


