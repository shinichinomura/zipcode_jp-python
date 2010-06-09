# -*- coding: utf-8 -*-

'''
Created on 2010/06/08

@author: Shinichi NOMURA (shinichi.nomura@gmail.com)
'''

from commands import getstatusoutput
from urllib import urlretrieve
import csv
import os
import re
import zenhan

ALL_DATA_URL = 'http://www.post.japanpost.jp/zipcode/dl/kogaki/lzh/ken_all.lzh'
ALL_DATA_CSV_NAME = 'ken_all.csv'

# ダウンロードしたLZHファイルを解凍するためのコマンド
# %s にファイル名が入る
UNLHA_COMMAND = 'lha x %s'

class CsvHandler (object):

    def __init__ (self):
        self.index = 0
        self.__reader = None
        self.__record = None
        self.__buffer = None
        
        self.unlha_command = UNLHA_COMMAND
        self.all_data_url = ALL_DATA_URL
        self.all_data_csv_name = ALL_DATA_CSV_NAME

    def open (self, filename=None):
        """
        郵便番号CSVの入力ストリームをオープンする
        
        @param filename CSVファイルのパス
                        指定しない場合はウェブサイトから自動的にダウンロードする
        """

        if filename is None:
            filename = self.__fetch_csv()

        self.__reader = csv.DictReader(file(filename), (
            # 全国地方公共団体コード
            'local_government_code',
            # (旧)郵便番号(5桁)
            'old_zipcode',
            # 郵便番号(7桁)
            'zipcode',
            # 都道府県名(カナ)
            'prefecture_kana',
            # 市区町村名(カナ)
            'city_kana',
            # 町域名(カナ)
            'local_area_kana',
            # 都道府県名
            'prefecture',
            # 市区町村名
            'city',
            # 町域名
            'local_area',
            # 一町域が二以上の郵便番号で表される場合の表示
            # 「1」は該当、「0」は該当せず 
            'is_separated',
            # 小字毎に番地が起番されている町域の表示
            # 「1」は該当、「0」は該当せず
            'has_banchi_per_koaza',
            # 丁目を有する町域の場合の表示
            # 「1」は該当、「0」は該当せず 
            'has_chome',
            # 一つの郵便番号で二以上の町域を表す場合の表示
            # 「1」は該当、「0」は該当せず
            'is_combined',
            # 更新の表示
            # 「0」は変更なし、「1」は変更あり、「2」廃止（廃止データのみ使用）  
            'is_updated',
            # 変更理由　
            # 「0」は変更なし、「1」市政・区政・町政・分区・政令指定都市施行、
            # 「2」住居表示の実施、「3」区画整理、「4」郵便区調整、集配局新設、
            # 「5」訂正、「6」廃止(廃止データのみ使用) 
            'update_code',
            ))


    def next (self):
        """
        レコードを一件取り出す
        
        分割レコードの結合などは済んだ状態で返す
        """
        record = None
        record = self.__next(record)

        record['index'] = self.index
        self.index += 1
        
        record['cleaned_local_area_kana'] = self.__clean_local_area_kana(record)
        record['cleaned_local_area'] = self.__clean_local_area(record)
        
        record['old_zipcode'] = record['old_zipcode'].strip()
        
        record['is_separated'] = int(record['is_separated'])
        record['has_banchi_per_koaza'] = int(record['has_banchi_per_koaza'])
        record['has_chome'] = int(record['has_chome'])
        record['is_combined'] = int(record['is_combined'])
        record['is_updated'] = int(record['is_updated'])
        record['update_code'] = int(record['update_code'])
        
        return record


    def __iter__ (self):
        return self


    def __next (self, record = None):
        if record is None:
            record = self.__buffer or self.__to_unicode(self.__reader.next())
        
        try:
            self.__buffer = self.__to_unicode(self.__reader.next())
        except StopIteration:
            self.__buffer = None
            return record
            
        if record['zipcode'] == self.__buffer['zipcode'] and int(self.__buffer['is_combined']) == 0:
            record['local_area_kana'] += self.__buffer['local_area_kana']
            record['local_area'] += self.__buffer['local_area']
            self.__buffer = None
            record = self.__next(record)
        
        return record


    def __to_unicode (self, record):
        for k, v in record.iteritems():
            if k in ('prefecture_kana', 'city_kana', 'local_area_kana'):
                record[k] = zenhan.h2z(unicode(v, 'shift-jis'), zenhan.ALL)
            elif k in ('prefecture', 'city', 'local_area'):
                record[k] = unicode(v, 'shift-jis')
        return record


    def __clean_local_area (self, record):
        """
        「以下に掲載がない場合」「（その他）」「〜一円」など、メタ情報を削除する
        """
        if record['local_area'].find(u"（") >= 0:
            return re.sub(u"（.*）", u"", record['local_area'])
        elif record['local_area'] == u"以下に掲載がない場合":
            return u""
        elif record['local_area'].find(u"の次に番地がくる場合") >= 0:
            return u""
        elif record['local_area'] != u"一円" and (record['city'] + u"一円").find(record['local_area']) > 0:
            return u""
        else:
            return record['local_area']


    def __clean_local_area_kana (self, record):
        """
        「イカニケイサイガナイバアイ」「（ソノタ）」「〜イチエン」など、メタ情報を削除する
        """
        if record['local_area_kana'].find(u"（") >= 0:
            return re.sub(u"\（.*\）", u"", record['local_area_kana'])
        elif record['local_area_kana'] == u"イカニケイサイガナイバアイ":
            return u""
        elif record['local_area_kana'].find(u"ノツギニバンチガクルバアイ") >= 0:
            return u""
        elif record['local_area_kana'] != u"イチエン" and (record['city_kana'] + u"イチエン").find(record['local_area_kana']) > 0:
            return u""
        else:
            return record['local_area_kana']
        
        
    def __fetch_csv (self, unlha_command=UNLHA_COMMAND):
        """
        CSVデータをダウンロード/解凍し、解凍後のファイルのパスを返す
        """
        filename, headers = urlretrieve(self.all_data_url) #@UnusedVariable
        current_dir = os.getcwd()
        os.chdir(os.path.dirname(filename))
        status, output = getstatusoutput(self.unlha_command % filename) #@UnusedVariable
        os.chdir(current_dir)

        return os.path.join(os.path.dirname(filename), self.all_data_csv_name)

