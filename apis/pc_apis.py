# encoding: utf-8
import json
import urllib
import requests
from xhs_utils.xhs_util import splice_str, generate_request_params, generate_x_b3_traceid
from loguru import logger
import random
import time

"""
    获小红书的api
    :param cookies_str: 你的cookies
"""
class XHS_Apis():
    def __init__(self):
        # 初始化基础 URL，这是小红书 API 请求的基础地址
        self.base_url = "https://edith.xiaohongshu.com"

    def get_user_info(self, user_id: str, cookies_str: str, proxies: dict = None):
        """
            获取用户的信息
            :param user_id: 你想要获取的用户的id
            :param cookies_str: 你的cookies
            :param proxies: 代理设置，默认为 None
            :return: 成功状态，消息，用户信息的 JSON 数据
        """
        res_json = None
        try:
            # 定义获取用户信息的 API 路径
            api = f"/api/sns/web/v1/user/otherinfo"
            # 构建请求参数
            params = {
                "target_user_id": user_id
            }
            # 拼接 API 路径和参数
            splice_api = splice_str(api, params)
            # 生成请求所需的头部、cookies 和数据
            headers, cookies, data = generate_request_params(cookies_str, splice_api)
            # 发送 GET 请求
            response = requests.get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            # 将响应内容解析为 JSON
            res_json = response.json()
            # 提取成功状态和消息
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            # 若出现异常，设置成功状态为 False，消息为异常信息
            success = False
            msg = str(e)
        return success, msg, res_json

    def get_user_note_info(self, user_id: str, cursor: str, cookies_str: str, xsec_token='', xsec_source='', proxies: dict = None):
        """
            获取用户指定位置的笔记
            :param user_id: 你想要获取的用户的id
            :param cursor: 你想要获取的笔记的cursor，用于分页
            :param cookies_str: 你的cookies
            :param xsec_token: xsec_token 参数，默认为空字符串
            :param xsec_source: xsec_source 参数，默认为空字符串
            :param proxies: 代理设置，默认为 None
            :return: 成功状态，消息，用户指定位置笔记信息的 JSON 数据
        """
        res_json = None
        try:
            # 定义获取用户笔记信息的 API 路径
            api = f"/api/sns/web/v1/user_posted"
            # 构建请求参数
            params = {
                "num": "30",
                "cursor": cursor,
                "user_id": user_id,
                "image_formats": "jpg,webp,avif",
                "xsec_token": xsec_token,
                "xsec_source": xsec_source,
            }
            # 拼接 API 路径和参数
            splice_api = splice_str(api, params)
            # 生成请求所需的头部、cookies 和数据
            headers, cookies, data = generate_request_params(cookies_str, splice_api)
            # 发送 GET 请求
            response = requests.get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            # 将响应内容解析为 JSON
            res_json = response.json()
            # 提取成功状态和消息
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            # 若出现异常，设置成功状态为 False，消息为异常信息
            success = False
            msg = str(e)
        return success, msg, res_json

    def get_user_all_notes(self, user_url: str, cookies_str: str, proxies: dict = None):
        """
           获取用户所有笔记
           :param user_url: 你想要获取的用户的 URL
           :param cookies_str: 你的cookies
           :param proxies: 代理设置，默认为 None
           :return: 成功状态，消息，用户所有笔记信息的列表
        """
        cursor = ''
        note_list = []
        try:
            # 解析用户 URL
            urlParse = urllib.parse.urlparse(user_url)
            # 提取用户 ID
            user_id = urlParse.path.split("/")[-1]
            # 解析 URL 中的查询参数
            kvs = urlParse.query.split('&')
            # 将查询参数转换为字典
            kvDist = {kv.split('=')[0]: kv.split('=')[1] for kv in kvs}
            # 提取 xsec_token 参数，若不存在则为空字符串
            xsec_token = kvDist['xsec_token'] if 'xsec_token' in kvDist else ""
            # 提取 xsec_source 参数，若不存在则为 'pc_search'
            xsec_source = kvDist['xsec_source'] if 'xsec_source' in kvDist else "pc_search"
            while True:
                # 调用 get_user_note_info 方法获取用户指定位置的笔记信息
                success, msg, res_json = self.get_user_note_info(user_id, cursor, cookies_str, xsec_token, xsec_source, proxies)
                if not success:
                    # 若请求失败，抛出异常
                    raise Exception(msg)
                # 提取笔记信息
                notes = res_json["data"]["notes"]
                if 'cursor' in res_json["data"]:
                    # 更新 cursor 用于下一页请求
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break
                # 将笔记信息添加到列表中
                note_list.extend(notes)
                if len(notes) == 0 or not res_json["data"]["has_more"]:
                    # 若没有更多笔记，退出循环
                    break
        except Exception as e:
            # 若出现异常，设置成功状态为 False，消息为异常信息
            success = False
            msg = str(e)
        return success, msg, note_list

    def get_note_info(self, url: str, cookies_str: str, proxies: dict = None):
        """
            获取笔记的详细信息
            :param url: 你想要获取的笔记的 URL
            :param cookies_str: 你的cookies
            :param proxies: 代理设置，默认为 None
            :return: 成功状态，消息，笔记详细信息的 JSON 数据
        """
        res_json = None
        try:
            time.sleep(random.randint(5, 10))
            # 解析笔记 URL
            urlParse = urllib.parse.urlparse(url)
            # 提取笔记 ID
            note_id = urlParse.path.split("/")[-1]
            # 解析 URL 中的查询参数
            kvs = urlParse.query.split('&')
            # 将查询参数转换为字典
            kvDist = {kv.split('=')[0]: kv.split('=')[1] for kv in kvs}
            # 定义获取笔记信息的 API 路径
            api = f"/api/sns/web/v1/feed"
            # 构建请求数据
            data = {
                "source_note_id": note_id,
                "image_formats": [
                    "jpg",
                    "webp",
                    "avif"
                ],
                "extra": {
                    "need_body_topic": "1"
                },
                "xsec_source": kvDist['xsec_source'] if 'xsec_source' in kvDist else "pc_search",
                "xsec_token": kvDist['xsec_token']
            }
            # 生成请求所需的头部、cookies 和数据
            headers, cookies, data = generate_request_params(cookies_str, api, data)
            # 发送 POST 请求
            response = requests.post(self.base_url + api, headers=headers, data=data, cookies=cookies, proxies=proxies)
            # 将响应内容解析为 JSON
            res_json = response.json()
            # 提取成功状态和消息
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            # 若出现异常，设置成功状态为 False，消息为异常信息
            success = False
            msg = str(e)
        return success, msg, res_json

    def get_search_keyword(self, word: str, cookies_str: str, proxies: dict = None):
        """
            获取搜索关键词相关信息
            :param word: 你的关键词
            :param cookies_str: 你的cookies
            :param proxies: 代理设置，默认为 None
            :return: 成功状态，消息，搜索关键词相关信息的 JSON 数据
        """
        res_json = None
        try:
            # 定义搜索关键词的 API 路径
            api = "/api/sns/web/v1/search/recommend"
            # 构建请求参数，对关键词进行 URL 编码
            params = {
                "keyword": urllib.parse.quote(word)
            }
            # 拼接 API 路径和参数
            splice_api = splice_str(api, params)
            # 生成请求所需的头部、cookies 和数据
            headers, cookies, data = generate_request_params(cookies_str, splice_api)
            # 发送 GET 请求
            response = requests.get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            # 将响应内容解析为 JSON
            res_json = response.json()
            # 提取成功状态和消息
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            # 若出现异常，设置成功状态为 False，消息为异常信息
            success = False
            msg = str(e)
        return success, msg, res_json

    def search_note(self, query: str, cookies_str: str, page=1, sort="general", note_type=0, proxies: dict = None):
        """
            获取搜索笔记的结果
            :param query: 搜索的关键词
            :param cookies_str: 你的 cookies
            :param page: 搜索的页数，默认为 1
            :param sort: 排序方式，general:综合排序, time_descending:时间排序, popularity_descending:热度排序，默认为 general
            :param note_type: 笔记类型，0:全部, 1:视频, 2:图文，默认为 0
            :param proxies: 代理设置，默认为 None
            :return: 成功状态，消息，搜索笔记结果的 JSON 数据
        """
        res_json = None
        try:
            # 定义搜索笔记的 API 路径
            api = "/api/sns/web/v1/search/notes"
            # 构建请求数据
            data = {
                "keyword": query,
                "page": page,
                "page_size": 20,
                "search_id": generate_x_b3_traceid(21),
                "sort": sort,
                "note_type": note_type,
                "ext_flags": [],
                "image_formats": [
                    "jpg",
                    "webp",
                    "avif"
                ]
            }
            # 生成请求所需的头部、cookies 和数据
            headers, cookies, data = generate_request_params(cookies_str, api, data)
            # 发送 POST 请求，对数据进行 UTF-8 编码
            response = requests.post(self.base_url + api, headers=headers, data=data.encode('utf-8'), cookies=cookies, proxies=proxies)
            # 将响应内容解析为 JSON
            res_json = response.json()
            # 提取成功状态和消息
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            # 若出现异常，设置成功状态为 False，消息为异常信息
            success = False
            msg = str(e)
        return success, msg, res_json

    def search_some_note(self, query: str, require_num: int, cookies_str: str, sort="general", note_type=0, proxies: dict = None):
        """
            指定数量搜索笔记，设置排序方式和笔记类型和笔记数量
            :param query: 搜索的关键词
            :param require_num: 搜索的数量
            :param cookies_str: 你的 cookies
            :param sort: 排序方式，general:综合排序, time_descending:时间排序, popularity_descending:热度排序，默认为 general
            :param note_type: 笔记类型，0:全部, 1:视频, 2:图文，默认为 0
            :param proxies: 代理设置，默认为 None
            :return: 成功状态，消息，搜索笔记结果的列表
        """
        page = 1
        note_list = []
        try:
            while True:
                # 调用 search_note 方法进行笔记搜索
                success, msg, res_json = self.search_note(query, cookies_str, page, sort, note_type, proxies)
                if not success:
                    # 若请求失败，抛出异常
                    raise Exception(msg)
                if "items" not in res_json["data"]:
                    # 若没有搜索结果，退出循环
                    break
                # 提取搜索结果中的笔记信息
                notes = res_json["data"]["items"]
                # 将笔记信息添加到列表中
                note_list.extend(notes)
                # 增加页码
                page += 1
                if len(note_list) >= require_num or not res_json["data"]["has_more"]:
                    # 若达到所需数量或没有更多结果，退出循环
                    break
        except Exception as e:
            # 若出现异常，设置成功状态为 False，消息为异常信息
            success = False
            msg = str(e)
        if len(note_list) > require_num:
            # 若笔记数量超过所需数量，截取前 require_num 条
            note_list = note_list[:require_num]
        return success, msg, note_list

    def get_note_out_comment(self, note_id: str, cursor: str, xsec_token: str, cookies_str: str, proxies: dict = None):
        """
            获取指定位置的笔记一级评论
            :param note_id: 笔记的 id
            :param cursor: 指定位置的评论的 cursor，用于分页
            :param xsec_token: xsec_token 参数
            :param cookies_str: 你的 cookies
            :param proxies: 代理设置，默认为 None
            :return: 成功状态，消息，指定位置笔记一级评论信息的 JSON 数据
        """
        res_json = None
        try:
            # 定义获取笔记一级评论的 API 路径
            api = "/api/sns/web/v2/comment/page"
            # 构建请求参数
            params = {
                "note_id": note_id,
                "cursor": cursor,
                "top_comment_id": "",
                "image_formats": "jpg,webp,avif",
                "xsec_token": xsec_token
            }
            # 拼接 API 路径和参数
            splice_api = splice_str(api, params)
            # 生成请求所需的头部、cookies 和数据
            headers, cookies, data = generate_request_params(cookies_str, splice_api)
            # 发送 GET 请求
            response = requests.get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            # 将响应内容解析为 JSON
            res_json = response.json()
            # 提取成功状态和消息
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            # 若出现异常，设置成功状态为 False，消息为异常信息
            success = False
            msg = str(e)
        return success, msg, res_json

    def get_note_all_out_comment(self, note_id: str, xsec_token: str, cookies_str: str, proxies: dict = None):
        """
            获取笔记的全部一级评论
            :param note_id: 笔记的 id
            :param xsec_token: xsec_token 参数
            :param cookies_str: 你的 cookies
            :param proxies: 代理设置，默认为 None
            :return: 成功状态，消息，笔记全部一级评论信息的列表
        """
        cursor = ''
        note_out_comment_list = []
        try:
            while True:
                # 调用 get_note_out_comment 方法获取指定位置的笔记一级评论信息
                success, msg, res_json = self.get_note_out_comment(note_id, cursor, xsec_token, cookies_str, proxies)
                if not success:
                    # 若请求失败，抛出异常
                    raise Exception(msg)
                # 提取评论信息
                comments = res_json["data"]["comments"]
                if 'cursor' in res_json["data"]:
                    # 更新 cursor 用于下一页请求
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break
                # 将评论信息添加到列表中
                note_out_comment_list.extend(comments)
                if len(note_out_comment_list) == 0 or not res_json["data"]["has_more"]:
                    # 若没有更多评论，退出循环
                    break
        except Exception as e:
            # 若出现异常，设置成功状态为 False，消息为异常信息
            success = False
            msg = str(e)
        return success, msg, note_out_comment_list

    def get_note_inner_comment(self, comment: dict, cursor: str, xsec_token: str, cookies_str: str, proxies: dict = None):
        """
            获取指定位置的笔记二级评论
            :param comment: 笔记的一级评论
            :param cursor: 指定位置的评论的 cursor，用于分页
            :param xsec_token: xsec_token 参数
            :param cookies_str: 你的 cookies
            :param proxies: 代理设置，默认为 None
            :return: 成功状态，消息，指定位置笔记二级评论信息的 JSON 数据
        """
        res_json = None
        try:
            # 定义获取笔记二级评论的 API 路径
            api = "/api/sns/web/v2/comment/sub/page"
            # 构建请求参数
            params = {
                "note_id": comment['note_id'],
                "root_comment_id": comment['id'],
                "num": "10",
                "cursor": cursor,
                "image_formats": "jpg,webp,avif",
                "top_comment_id": '',
                "xsec_token": xsec_token
            }
            # 拼接 API 路径和参数
            splice_api = splice_str(api, params)
            # 生成请求所需的头部、cookies 和数据
            headers, cookies, data = generate_request_params(cookies_str, splice_api)
            # 发送 GET 请求
            response = requests.get(self.base_url + splice_api, headers=headers, cookies=cookies, proxies=proxies)
            # 将响应内容解析为 JSON
            res_json = response.json()
            # 提取成功状态和消息
            success, msg = res_json["success"], res_json["msg"]
        except Exception as e:
            # 若出现异常，设置成功状态为 False，消息为异常信息
            success = False
            msg = str(e)
        return success, msg, res_json

    def get_note_all_inner_comment(self, comment: dict, xsec_token: str, cookies_str: str, proxies: dict = None):
        """
            获取笔记的全部二级评论
            :param comment: 笔记的一级评论
            :param xsec_token: xsec_token 参数
            :param cookies_str: 你的 cookies
            :param proxies: 代理设置，默认为 None
            :return: 成功状态，消息，包含全部二级评论信息的一级评论字典
        """
        try:
            if not comment['sub_comment_has_more']:
                # 若没有更多二级评论，直接返回成功信息
                return True, 'success', comment
            # 获取二级评论的起始 cursor
            cursor = comment['sub_comment_cursor']
            inner_comment_list = []
            while True:
                # 调用 get_note_inner_comment 方法获取指定位置的笔记二级评论信息
                success, msg, res_json = self.get_note_inner_comment(comment, cursor, xsec_token, cookies_str, proxies)
                if not success:
                    # 若请求失败，抛出异常
                    raise Exception(msg)
                # 提取评论信息
                comments = res_json["data"]["comments"]
                if 'cursor' in res_json["data"]:
                    # 更新 cursor 用于下一页请求
                    cursor = str(res_json["data"]["cursor"])
                else:
                    break
                # 将评论信息添加到列表中
                inner_comment_list.extend(comments)
                if not res_json["data"]["has_more"]:
                    # 若没有更多评论，退出循环
                    break
            # 将二级评论信息添加到一级评论的 sub_comments 列表中
            comment['sub_comments'].extend(inner_comment_list)
        except Exception as e:
            # 若出现异常，设置成功状态为 False，消息为异常信息
            success = False
            msg = str(e)
        return success, msg, comment

    def get_note_all_comment(self, url: str, cookies_str: str, proxies: dict = None):
        """
            获取一篇文章的所有评论
            :param url: 你想要获取的笔记的 URL
            :param cookies_str: 你的 cookies
            :param proxies: 代理设置，默认为 None
            :return: 成功状态，消息，文章所有评论信息的列表
        """
        out_comment_list = []
        try:
            # 解析笔记 URL
            urlParse = urllib.parse.urlparse(url)
            # 提取笔记 ID
            note_id = urlParse.path.split("/")[-1]
            # 解析 URL 中的查询参数
            kvs = urlParse.query.split('&')
            # 将查询参数转换为字典
            kvDist = {kv.split('=')[0]: kv.split('=')[1] for kv in kvs}
            # 调用 get_note_all_out_comment 方法获取笔记的全部一级评论信息
            success, msg, out_comment_list = self.get_note_all_out_comment(note_id, kvDist['xsec_token'], cookies_str, proxies)
            if not success:
                # 若请求失败，抛出异常
                raise Exception(msg)
            for comment in out_comment_list:
                # 调用 get_note_all_inner_comment 方法获取每条一级评论的全部二级评论信息
                success, msg, new_comment = self.get_note_all_inner_comment(comment, kvDist['xsec_token'], cookies_str, proxies)
                if not success:
                    # 若请求失败，抛出异常
                    raise Exception(msg)
        except Exception as e:
            # 若出现异常，设置成功状态为 False，消息为异常信息
            success = False
            msg = str(e)
        return success, msg, out_comment_list





if __name__ == '__main__':
    xhs_apis = XHS_Apis()
    cookies_str = r'abRequestId=de8e5d86-5e27-5b31-8ca2-b73cd17cb3d6; webBuild=4.60.1; xsecappid=xhs-pc-web; loadts=1742441204331; a1=195b196ca6brfvm416zq97vun6jks0he57q6dzvnq50000330801; webId=c3d5cbc034ea9702dec83fbca305268a; websectiga=9730ffafd96f2d09dc024760e253af6ab1feb0002827740b95a255ddf6847fc8; gid=yj2DyjKfYd2iyj2DyjKS0WuhKDFih64yKuAjAIAWh7IKVK28TM8xdf888qq8Y8y8J0j0JiSJ; web_session=0400698df4f18f0a343071c3ee354b0cffbd0b; unread={%22ub%22:%2267d40aec000000001b03cd53%22%2C%22ue%22:%2267ca9b3f0000000028029e78%22%2C%22uc%22:33}'
    # # 获取用户信息
    # user_url = 'https://www.xiaohongshu.com/user/profile/67a332a2000000000d008358?xsec_token=ABTf9yz4cLHhTycIlksF0jOi1yIZgfcaQ6IXNNGdKJ8xg=&xsec_source=pc_feed'
    # success, msg, user_info = xhs_apis.get_user_info('67a332a2000000000d008358', cookies_str)
    # logger.info(f'获取用户信息结果 {json.dumps(user_info, ensure_ascii=False)}: {success}, msg: {msg}')
    # success, msg, note_list = xhs_apis.get_user_all_notes(user_url, cookies_str)
    # logger.info(f'获取用户所有笔记结果 {json.dumps(note_list, ensure_ascii=False)}: {success}, msg: {msg}')
    # # 获取笔记信息
    # note_url = r'https://www.xiaohongshu.com/explore/67d7c713000000000900e391?xsec_token=AB1ACxbo5cevHxV_bWibTmK8R1DDz0NnAW1PbFZLABXtE=&xsec_source=pc_user'
    # success, msg, note_info = xhs_apis.get_note_info(note_url, cookies_str)
    # logger.info(f'获取笔记信息结果 {json.dumps(note_info, ensure_ascii=False)}: {success}, msg: {msg}')
    # # 获取搜索关键词
    # query = "榴莲"
    # success, msg, search_keyword = xhs_apis.get_search_keyword(query, cookies_str)
    # logger.info(f'获取搜索关键词结果 {json.dumps(search_keyword, ensure_ascii=False)}: {success}, msg: {msg}')
    # # 搜索笔记
    # query = "榴莲"
    # query_num = 10
    # sort = "general"
    # note_type = 0
    # success, msg, notes = xhs_apis.search_some_note(query, query_num, cookies_str, sort, note_type)
    # logger.info(f'搜索笔记结果 {json.dumps(notes, ensure_ascii=False)}: {success}, msg: {msg}')
    # 获取笔记评论
    note_url = r'https://www.xiaohongshu.com/explore/678ddb44000000001b00a0bb?xsec_token=ABOm-mzcaX0ghyz9OA_YNAjYJ8cLG7ePBl44ZxirCwWEQ='
    success, msg, note_all_comment = xhs_apis.get_note_all_comment(note_url, cookies_str)
    logger.info(f'获取笔记评论结果 {json.dumps(note_all_comment, ensure_ascii=False)}: {success}, msg: {msg}')




