import os
from loguru import logger
from apis.pc_apis import XHS_Apis
from xhs_utils.common_utils import init
from xhs_utils.data_util import handle_note_info, download_note, save_to_xlsx
import random
import time


class Data_Spider():
    def __init__(self):
        # 初始化 XHS_Apis 类的实例，用于调用小红书相关的 API
        self.xhs_apis = XHS_Apis()

    def spider_note(self, note_url: str, cookies_str: str, proxies=None):
        """
        爬取一个笔记的信息
        :param note_url: 笔记的 URL
        :param cookies_str: 用户的 cookies 字符串
        :param proxies: 代理设置，默认为 None
        :return: 爬取结果的成功状态、消息和笔记信息
        """
        note_info = None
        try:
            # 调用 XHS_Apis 类的 get_note_info 方法获取笔记信息
            success, msg, note_info = self.xhs_apis.get_note_info(note_url, cookies_str, proxies)
            if success:
                # 提取笔记信息
                note_info = note_info['data']['items'][0]
                # 添加笔记的 URL 到信息中
                note_info['url'] = note_url
                # 处理笔记信息
                note_info = handle_note_info(note_info)
        except Exception as e:
            # 若出现异常，标记为失败并记录异常信息
            success = False
            msg = e
        # 记录爬取笔记信息的结果
        logger.info(f'爬取笔记信息 {note_url}: {success}, msg: {msg}')
        return success, msg, note_info

    def spider_some_note(self, notes: list, cookies_str: str, base_path: dict, save_choice: str, excel_name: str = '',
                         proxies=None):
        """
        爬取一些笔记的信息
        :param notes: 笔记 URL 的列表
        :param cookies_str: 用户的 cookies 字符串
        :param base_path: 保存路径的字典
        :param save_choice: 保存选项，可选值为 'all', 'media', 'excel'
        :param excel_name: 保存 Excel 文件的名称，默认为空
        :param proxies: 代理设置，默认为 None
        :return: 无
        """
        # 检查保存选项为 'all' 或 'excel' 时，Excel 文件名是否为空
        if (save_choice == 'all' or save_choice == 'excel') and excel_name == '':
            raise ValueError('excel_name 不能为空')
        note_list = []
        for note_url in notes:
            # 调用 spider_note 方法爬取单个笔记的信息
            success, msg, note_info = self.spider_note(note_url, cookies_str, proxies)
            if note_info is not None and success:
                # 将成功爬取的笔记信息添加到列表中
                note_list.append(note_info)
        for note_info in note_list:
            if save_choice == 'all' or save_choice == 'media':
                # 下载笔记的媒体文件
                download_note(note_info, base_path['media'])
        if save_choice == 'all' or save_choice == 'excel':
            # 构建 Excel 文件的完整路径
            file_path = os.path.abspath(os.path.join(base_path['excel'], f'{excel_name}.xlsx'))
            # 将笔记信息保存到 Excel 文件中
            save_to_xlsx(note_list, file_path)

    def spider_user_all_note(self, user_url: str, cookies_str: str, base_path: dict, save_choice: str,
                             excel_name: str = '', proxies=None, note_num=10):
        """
        爬取一个用户的所有笔记
        :param user_url: 用户的 URL
        :param cookies_str: 用户的 cookies 字符串
        :param base_path: 保存路径的字典
        :param save_choice: 保存选项，可选值为 'all', 'media', 'excel'
        :param excel_name: 保存 Excel 文件的名称，默认为空
        :param proxies: 代理设置，默认为 None
        :param note_num: 笔记数量，默认为 10
        :return: 爬取的笔记 URL 列表、成功状态和消息
        """
        note_list = []
        try:
            # 调用 XHS_Apis 类的 get_user_all_notes 方法获取用户的所有笔记信息
            success, msg, all_note_info = self.xhs_apis.get_user_all_notes(user_url, cookies_str, proxies)
            if success:
                # 记录用户的作品数量
                logger.info(f'用户 {user_url} 作品数量: {len(all_note_info)}')
                count = 0
                for simple_note_info in all_note_info:
                    # 构建笔记的 URL
                    note_url = f"https://www.xiaohongshu.com/explore/{simple_note_info['note_id']}?xsec_token={simple_note_info['xsec_token']}"
                    # 将笔记 URL 添加到列表中
                    note_list.append(note_url)
                    count = count + 1
                    if count >= note_num:
                        break
            if save_choice == 'all' or save_choice == 'excel':
                # 若保存选项为 'all' 或 'excel'，设置 Excel 文件名
                excel_name = user_url.split('/')[-1].split('?')[0]
            # 调用 spider_some_note 方法爬取这些笔记的信息
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies)
        except Exception as e:
            # 若出现异常，标记为失败并记录异常信息
            success = False
            msg = e
        # 记录爬取用户所有笔记的结果
        logger.info(f'爬取用户所有视频 {user_url}: {success}, msg: {msg}')
        return note_list, success, msg

    def spider_some_search_note(self, query: str, require_num: int, cookies_str: str, base_path: dict, save_choice: str,
                                sort="general", note_type=0, excel_name: str = '', proxies=None):
        """
            指定数量搜索笔记，设置排序方式和笔记类型和笔记数量
            :param query 搜索的关键词
            :param require_num 搜索的数量
            :param cookies_str 你的cookies
            :param base_path 保存路径
            :param sort 排序方式 general:综合排序, time_descending:时间排序, popularity_descending:热度排序
            :param note_type 笔记类型 0:全部, 1:视频, 2:图文
            :param excel_name 保存 Excel 文件的名称，默认为空
            :param proxies 代理设置，默认为 None
            返回搜索的结果
        """
        note_list = []
        try:
            # 调用 XHS_Apis 类的 search_some_note 方法搜索笔记
            success, msg, notes = self.xhs_apis.search_some_note(query, require_num, cookies_str, sort, note_type,
                                                                 proxies)
            if success:
                # 过滤出笔记类型的数据
                notes = list(filter(lambda x: x['model_type'] == "note", notes))
                # 记录搜索到的笔记数量
                logger.info(f'搜索关键词 {query} 笔记数量: {len(notes)}')
                for note in notes:
                    # 构建笔记的 URL
                    note_url = f"https://www.xiaohongshu.com/explore/{note['id']}?xsec_token={note['xsec_token']}"
                    # 将笔记 URL 添加到列表中
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                # 若保存选项为 'all' 或 'excel'，设置 Excel 文件名
                excel_name = query
            # 调用 spider_some_note 方法爬取这些笔记的信息
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies)
        except Exception as e:
            # 若出现异常，标记为失败并记录异常信息
            success = False
            msg = e
        # 记录搜索笔记的结果
        logger.info(f'搜索关键词 {query} 笔记: {success}, msg: {msg}')
        return note_list, success, msg


if __name__ == '__main__':
    cookies_str, base_path = init()
    data_spider = Data_Spider()
    # save_choice: all: 保存所有的信息, media: 保存视频和图片, excel: 保存到excel
    # save_choice 为 excel 或者 all 时，excel_name 不能为空
    # 1
    # notes = [
    #     r'https://www.xiaohongshu.com/explore/67d7c713000000000900e391?xsec_token=AB1ACxbo5cevHxV_bWibTmK8R1DDz0NnAW1PbFZLABXtE=&xsec_source=pc_user',
    # ]
    # data_spider.spider_some_note(notes, cookies_str, base_path, 'all', 'test')

    # 2
    user_url = r'https://www.xiaohongshu.com/user/profile/5965ebab50c4b438acc7a2e4?xsec_token=ABG-hrWDPgpak9xJtc2hNVsoGh3pLhem858oPGGGkBy04=&xsec_source=pc_feed'
    data_spider.spider_user_all_note(user_url, cookies_str, base_path, 'all','','',20)

    # 3
    # query = "酒店洗浴用品报价"
    # query_num = 5
    # sort = "popularity_descending"
    # note_type = 2
    # data_spider.spider_some_search_note(query, query_num, cookies_str, base_path, 'all', sort, note_type)
