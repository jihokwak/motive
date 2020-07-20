from slacker import Slacker

class SlackBot :

    @staticmethod
    def send_msg(msg, token) :
        slack = Slacker(token)
        print(msg)
        slack.chat.post_message(
            channel='datacenter-app',
            text=msg,
            as_user=True
        )
    @classmethod
    def deco_sender(cls, msg, token):
        def wrapper(func) :
            def decorator(*args, **kwargs) :
                cls.send_msg(msg + " started!", token)
                result = func(*args, **kwargs)
                cls.send_msg(msg + " finished!", token)
                return result
            return decorator
        return wrapper

