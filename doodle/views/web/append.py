# -*- coding: utf-8 -*-

from tornado.web import HTTPError

from doodle.common.url import URL_PATTERN
from doodle.config import CONFIG

from ..base_handler import UserHandler


class PageAppendHandler(UserHandler):
    def get(self):
        self.set_cache(is_public=False)

        if not self.referer:
            raise HTTPError(403)
        match = URL_PATTERN.match(self.referer)
        if not match:
            raise HTTPError(403)
        referer_host = match.group('host')
        if not referer_host:
            raise HTTPError(403)
        host = self.request.headers.get('Host')
        if host != referer_host:
            raise HTTPError(403)

        if self.get_cookie('session_time'):
            self.clear_cookie('session_time')  # session_time 的作用是让用户重新访问这个接口，既然已经在访问了，也就可以清除掉了

        output = {}
        if self.current_user:
            output['has_logged_in'] = 1
            output['user_name'] = self.current_user.name
            output['logout_url'] = CONFIG.BLOG_HOME_RELATIVE_PATH + 'logout'
            output['profile_url'] = CONFIG.BLOG_HOME_RELATIVE_PATH + 'profile'
            output['comment_url_prefix'] = CONFIG.BLOG_HOME_RELATIVE_PATH + 'comment/'
            extension = '.js' if CONFIG.DEBUG_MODE else '.min.js'
            output['article_js_urls'] = [
                '%s%s%s' % (CONFIG.BLOG_HOME_RELATIVE_PATH, js_path, extension)
                for js_path in (
                    'static/markitup/jquery.markitup',
                    'static/markitup/sets/bbcode/set',
                    'static/theme/null/js/msgbox'
                )
            ]
            if self.is_admin:
                output['is_admin'] = 1
                output['admin_url'] = CONFIG.BLOG_ADMIN_RELATIVE_PATH
                output['edit_url_prefix'] = CONFIG.BLOG_ADMIN_RELATIVE_PATH + 'article/'
        else:
            output['login_url'] = CONFIG.LOGIN_URL

        self.write_json(output)
