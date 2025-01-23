import os
from pathlib import Path
from load import get_pdf_document_paths
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTTextLineHorizontal, LTChar
import pdfplumber

def extract_bold_titles_with_comma_merge(pdf_path):
    """
    從 PDF 中提取粗體字標題，基於字體大小組合標題，並合併逗號結尾行與下一行。
    :param pdf_path: PDF 文件路徑
    :return: 包含完整標題的列表
    """
    bold_titles = []
    temp_title = ""  # 臨時存儲多行標題
    prev_font_size = None  # 上一行的字體大小
    merge_next = False  # 是否將下一行合併到當前行

    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                for text_line in element:
                    if isinstance(text_line, LTTextLineHorizontal):
                        is_bold = False
                        line_text = ""
                        font_size = None  # 當前行的字體大小

                        for char in text_line:
                            if isinstance(char, LTChar):
                                # 設置當前字體大小
                                if font_size is None:
                                    font_size = round(char.size, 2)  # 四捨五入保留2位小數
                                # 判斷是否為粗體
                                if "Bold" in char.fontname:
                                    is_bold = True
                                line_text += char.get_text()

                        # 如果當前行是粗體，處理標題組合
                        if is_bold:
                            line_text = line_text.strip()  # 去除首尾空白

                            if merge_next:
                                # 合併上一行逗號結尾與當前行
                                temp_title += " " + line_text
                                merge_next = False
                            elif prev_font_size is None or font_size == prev_font_size:
                                # 字體大小相同，合併為一段
                                temp_title += " " + line_text if temp_title else line_text
                            else:
                                # 字體大小不同，存儲上一段標題
                                if temp_title:
                                    bold_titles.append(temp_title.strip())
                                temp_title = line_text

                            # 如果當前行以逗號結尾，標記與下一行合併
                            if line_text.endswith(","):
                                merge_next = True

                            prev_font_size = font_size  # 更新上一行字體大小
                        else:
                            # 遇到非粗體行，存儲已完成的標題
                            if temp_title:
                                bold_titles.append(temp_title.strip())
                                temp_title = ""
                            prev_font_size = None

    # 添加最後的臨時標題
    if temp_title:
        bold_titles.append(temp_title.strip())

    return bold_titles

def merge_title(bold_titles):
    index = 0
        
    while index < len(bold_titles) - 1:
        if bold_titles[index].endswith(","):
            # 合併當前標題與下一標題，並取代當前標題
            bold_titles[index] += " " + bold_titles[index + 1]
            del bold_titles[index + 1]  # 刪除已合併的下一標題
        else:
            index += 1
    
    return bold_titles

def extract_table_with_pdfplumber_to_list(pdf_path):
    all_tables = []  # 存儲所有頁面的表格

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"正在處理第 {i+1} 頁...")
            table = page.extract_table()  # 提取表格
            if table:
                # 過濾掉表格中的 None 和空字符串
                filtered_table = [
                    [cell for cell in row if cell]  # 僅保留有數據的單元格
                    for row in table
                    if any(cell for cell in row)  # 僅保留有數據的行
                ]

                # 如果表格還有內容，才加入列表
                if filtered_table:
                    all_tables.append(filtered_table)
                    print(f"第 {i+1} 頁表格（過濾後）:\n{filtered_table}\n")

    return all_tables  # 返回純淨的表格列表

def clean_titles(titles, tables):
    """
    從 titles 中移除出現在 tables 中的內容。
    tables 的文字會去除空格並合併，作為過濾基準。
    titles 中的內容如果包含表格的任何文字（子集合檢查），則移除。

    :param titles: 原始粗體標題列表 (1D list)
    :param tables: 表格數據 (嵌套列表形式的表格)
    :return: 過濾後的粗體標題列表
    """

    def normalize_table_text(text):
        """
        將表格文字中的空格移除並合併。
        :param text: 表格中的文字
        :return: 合併後的文字
        """
        return text.replace(" ", "")  # 移除所有空格

    # 將表格內容合併處理，生成過濾基準集合
    table_texts = set(
        normalize_table_text(cell)
        for table in tables
        for row in table
        for cell in row if cell
    )

    # 過濾 titles 中出現在表格內容的部分
    filtered_titles = []
    for title in titles:
        # 移除空格，並檢查是否包含表格文字
        if not any(table_text in title.replace(" ", "") for table_text in table_texts):
            filtered_titles.append(title)

    return filtered_titles

def filter_titles(file_path):
    titles = extract_bold_titles_with_comma_merge(file_path)
    titles = merge_title(titles)
    tables = extract_table_with_pdfplumber_to_list(file_path)
    filtered_titles = clean_titles(titles, tables)
    return filtered_titles

if __name__ == '__main__':
    AGENT_ROOT = Path(__file__).resolve().parents[1]
    folder_path = AGENT_ROOT / "documents" / "system"
    pdf_files = get_pdf_document_paths(folder_path)
    test_file = pdf_files[1]
    filtered_titles = filter_titles(test_file)
    print("Filtered Titles:",  filtered_titles)
    

