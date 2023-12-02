from app import App
import logic


class AppService:
    def send_request(self, ad_classification, time=None):
        # if we use real-time data, time will be None.
        # if we use historical intervals, time will be a string like '13:45'.
        map_data = logic.process_request(ad_classification, time)
        return map_data


if __name__ == '__main__':
    request_handler = AppService()
    app = App(request_handler)
    app.run()



