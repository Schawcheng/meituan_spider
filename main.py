import datetime
import json
import traceback

import config.common
import tools
import utils.database
import spider.order
import spider.comment


def insert_order_in_7(cookie):
    db = utils.database.get_db()

    orders = spider.order.get_orders_in_7(cookie)

    for item in orders:
        item = json.loads(item['orderInfo'])
        cursor = db.cursor()

        platform = 'MT'
        order_seq = None
        order_no = None
        order_amount = None
        pay_amount = None
        income = None
        user_type = None
        user_info = None
        food_details = None
        poi_id = None
        create_time = None

        if 'orderInfo' not in item:
            order_seq = item['wm_poi_order_dayseq']
            order_no = item['wm_order_id_view_str']
            order_amount = item['cartDetailVos'][0]['cartAmount']
            pay_amount = item['total_after']
            income = item['total_after']
            user_type = '未知'
            user_info = json.dumps(
                {'recipientName': item['recipient_name'],
                 'recipientPhoneVo': {'appRecipientPhoneVo': {'recipientPhoneShow': item['recipient_phone']}}}).replace(
                '\\u', '\\\\u')
            food_details = item['cartDetailVos'][0]['details']
            food_details = list(map(lambda x: {'foodName': x['food_name'], 'count': x['count'], 'foodId': x['wm_food_id']}, food_details))
            food_details = json.dumps(food_details).replace('\\u', '\\\\u')
            poi_id = item['wm_poi_id']
            create_time = datetime.datetime.fromtimestamp(item['order_time'])
        else:
            order_seq = item['orderInfo']['dayseq']
            order_no = item['orderInfo']['wmOrderViewId']
            order_amount = item['chargeInfo']['fixedSettlementInfo']['foodAmount']
            pay_amount = item['chargeInfo']['fixedSettlementInfo']['userPayTotalAmount']
            income = item['chargeInfo']['fixedSettlementInfo']['settleAmount']
            user_type = item['foodInfo']['userLabelVo']['contents'][0]['info']
            user_info = json.dumps(item['userInfo']).replace('\\u', '\\\\u')
            food_details = item['foodInfo']['cartDetailVos'][0]['details']
            food_details = list(
                map(lambda item: {'foodName': item['foodName'], 'count': item['count'], 'foodId': item['foodId']},
                    food_details))
            food_details = json.dumps(food_details).replace('\\u', '\\\\u')
            poi_id = item['orderInfo']['basicVo']['wmPoiId']
            create_time = item['orderInfo']['basicVo']['orderTime']
            create_time = datetime.datetime.fromtimestamp(create_time)

        try:
            query_sql = f'select count(*) from mt_order where order_no={order_no}'
            cursor.execute(query_sql)
            count = cursor.fetchone()[0]
            if count > 0:
                update_sql = f"""update mt_order set food_details='{food_details}' where order_no={order_no}"""
                cursor.execute(update_sql)
                db.commit()
                # print(update_sql)
                continue

            insert_sql = f"""insert into mt_order(
                             platform, 
                             order_seq, 
                             order_no, 
                             order_amount, 
                             pay_amount, 
                             income, 
                             user_type, 
                             user_info,
                             food_details,
                             poi_id,
                             create_time) values(
                             '{platform}',
                             '{order_seq}',
                             '{order_no}',
                             '{order_amount}',
                             '{pay_amount}',
                             '{income}',
                             '{user_type}',
                             '{user_info}',
                             '{food_details}',
                             '{poi_id}',
                             '{create_time}'
                             )
            """
            cursor.execute(insert_sql)
            db.commit()
            # print(f'成功插入订单{order_no}')

        except Exception as e:
            db.rollback()
            traceback.print_exc()
        finally:
            cursor.close()
    db.close()


def insert_comment_in_180(cookie, comment_type):
    db = utils.database.get_db()

    comments = spider.comment.get_comments_in_180(cookie, comment_type)

    for comment in comments:
        comment_id = comment['id']
        poi_id = comment['wmPoiId']
        user_name = comment['userName']
        content = comment['comment']
        order_details = json.dumps(comment['orderDetails']).replace('\\u', '\\\\u')
        score = comment['orderCommentScore']
        create_time = tools.str2date(comment['createTime'])

        cursor = db.cursor()
        try:
            query_sql = f"select count(*) from comment where comment_id='{comment_id}'"
            cursor.execute(query_sql)
            count = cursor.fetchone()[0]
            if count > 0:
                update_sql = f"update comment set order_details='{order_details}', score='{score}' where comment_id='{comment_id}'"
                # print(update_sql)
                cursor.execute(update_sql)
                db.commit()
                continue

            insert_sql = f"""insert into comment(
            comment_id, 
            poi_id, 
            user_name, 
            content, 
            order_details, 
            comment_type,
            score,
            create_time) values(
            '{comment_id}', 
            '{poi_id}', 
            '{user_name}',
            '{content}', 
            '{order_details}', 
            '{comment_type}',
            '{score}',
            '{create_time}'
            )
            """
            cursor.execute(insert_sql)
            db.commit()
            # print(f'成功插入评论: {comment_id}')
        except Exception as e:
            traceback.print_exc(e)
        finally:
            cursor.close()

    db.close()


def insert_orders_for_malls():
    db = utils.database.get_db()

    try:
        query_sql = f"select * from mall"
        cursor = db.cursor()
        cursor.execute(query_sql)
        malls = cursor.fetchall()
        for mall in malls:
            insert_order_in_7(mall[3])
            insert_comment_in_180(mall[3], 3)
    except Exception as e:
        traceback.print_exc(e)


if __name__ == '__main__':
    # insert_into_order_in_7()
    insert_orders_for_malls()
