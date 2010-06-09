# -*- coding: utf-8 -*-

'''
Created on 2010/06/08

@author: Shinichi NOMURA (shinichi.nomura@gmail.com)
'''

from zipcode_jp.data_handler import CsvHandler
import os
import unittest

class TestZipcodeJp (unittest.TestCase):
    
    def testnext (self):
        csv_handler = CsvHandler()
        csv_handler.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.csv'))
    
        # 普通
        record = csv_handler.next()
        self.assertEqual(0, record['index'])
        self.assertEqual(u"01224", record['local_government_code'])
        self.assertEqual(u"066", record['old_zipcode'])
        self.assertEqual(u"0660015", record['zipcode'])
        self.assertEqual(u"北海道", record['prefecture'])
        self.assertEqual(u"千歳市", record['city'])
        self.assertEqual(u"青葉", record['local_area'])
        self.assertEqual(u"青葉", record['cleaned_local_area'])
        self.assertEqual(u"ホッカイドウ", record['prefecture_kana'])
        self.assertEqual(u"チトセシ", record['city_kana'])
        self.assertEqual(u"アオバ", record['local_area_kana'])
        self.assertEqual(u"アオバ", record['cleaned_local_area_kana'])
        self.assertEqual(0, record['is_separated'])
        self.assertEqual(0, record['has_banchi_per_koaza'])
        self.assertEqual(1, record['has_chome'])
        self.assertEqual(0, record['is_combined'])
        self.assertEqual(0, record['is_updated'])
        self.assertEqual(0, record['update_code'])
        
        # （）あり
        record = csv_handler.next()
        self.assertEqual(u"本郷通（南）", record['local_area'])
        self.assertEqual(u"本郷通", record['cleaned_local_area'])
        self.assertEqual(u"ホンゴウドオリ（ミナミ）", record['local_area_kana'])
        self.assertEqual(u"ホンゴウドオリ", record['cleaned_local_area_kana'])
    
        # 以下に掲載がない場合
        record = csv_handler.next()
        self.assertEqual(u"以下に掲載がない場合", record['local_area'])
        self.assertEqual(u"", record['cleaned_local_area'])
        self.assertEqual(u"イカニケイサイガナイバアイ", record['local_area_kana'])
        self.assertEqual(u"", record['cleaned_local_area_kana'])
        
        # 複数行連結
        record = csv_handler.next()
        self.assertEqual(3, record['index'])
        self.assertEqual(u"協和（８８−２、２７１−１０、３４３−２、４０４−１、４２７−３、４３１−１２、４４３−６、６０８−２、６４１−８、８１４、８４２−５、１１３７−３、１３９２、１６５７、１７５２番地）", record['local_area'])
        self.assertEqual(u"協和", record['cleaned_local_area'])
        self.assertEqual(u"キョウワ（８８−２、２７１−１０、３４３−２、４０４−１、４２７−３、４３１−１２、４４３−６、６０８−２、６４１−８、８１４、８４２−５、１１３７−３、１３９２、１６５７、１７５２バンチ）", record['local_area_kana'])
        self.assertEqual(u"キョウワ", record['cleaned_local_area_kana'])
        
        # 郵便番号重複
        record = csv_handler.next()
        self.assertEqual(4, record['index'])
        self.assertEqual(u"南部青葉町", record['local_area'])
        self.assertEqual(u"ナンブアオバチョウ", record['local_area_kana'])
        
        # 同上
        record = csv_handler.next()
        self.assertEqual(u"南部菊水町", record['local_area'])
        self.assertEqual(u"ナンブキクスイチョウ", record['local_area_kana'])
        
        # 〜一円
        record = csv_handler.next()
        self.assertEqual(u"姫島村一円", record['local_area'])
        self.assertEqual(u"", record['cleaned_local_area'])
        self.assertEqual(u"ヒメシマムライチエン", record['local_area_kana'])
        self.assertEqual(u"", record['cleaned_local_area_kana'])
        
        # 〜の次に番地がくる場合
        record = csv_handler.next()
        self.assertEqual(u"日出町の次に番地がくる場合", record['local_area'])
        self.assertEqual(u"", record['cleaned_local_area'])
        self.assertEqual(u"ヒジマチノツギニバンチガクルバアイ", record['local_area_kana'])
        self.assertEqual(u"", record['cleaned_local_area_kana'])
        
        # 地名としての「一円」
        record = csv_handler.next()
        self.assertEqual(u"一円", record['local_area'])
        self.assertEqual(u"一円", record['cleaned_local_area'])
        self.assertEqual(u"イチエン", record['local_area_kana'])
        self.assertEqual(u"イチエン", record['cleaned_local_area_kana'])
        
if __name__ == '__main__':
    unittest.main()
