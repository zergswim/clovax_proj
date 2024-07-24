def split_paragraphs(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # 텍스트를 줄 단위로 분리
    lines = text.split('\n')

    # 빈 줄을 기준으로 문단 구분
    paragraphs = []
    current_paragraph = []
    for line in lines:
        if line.strip() == '':
            if current_paragraph:
                paragraphs.append('\n'.join(current_paragraph))
                current_paragraph = []
        else:
            current_paragraph.append(line)

    # 마지막 문단 추가
    if current_paragraph:
        paragraphs.append('\n'.join(current_paragraph))

    return paragraphs


if __name__ == '__main__':
    # 사용 예시
    file_path = 'Faust.txt'
    paragraphs = split_paragraphs(file_path)
    
    # 문단 출력
    for paragraph in paragraphs:
        print(paragraph)
        print()
