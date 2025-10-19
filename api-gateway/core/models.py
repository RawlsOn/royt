from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db import models
import base.models as base_models
import uuid
from django.db.models.signals import post_save

import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

import user.models as user_models

# ./manage.py makemigrations core
# ./manage.py migrate core --database=core

class ArticleBase(base_models.RoBase):
    article_id = models.CharField(max_length= 16, primary_key=True)
    lgeo = models.CharField(max_length= 16, blank=True, null=True)

    title = models.CharField(max_length= 255, blank=True, null=True)
    build_name = models.CharField(max_length= 255, blank=True, null=True)
    vrfcTpCd = models.CharField(max_length= 16, blank=True, null=True)
    rletTpNm = models.CharField(max_length= 32, blank=True, null=True)
    확인날짜 = models.DateField(blank=True, null=True)
    중요설명 = models.CharField(max_length= 255, blank=True, null=True)
    종류 = models.CharField(max_length= 8, blank=True, null=True, db_index=True)
    거래타입 = models.CharField(max_length= 8, blank=True, null=True, db_index=True)
    cortarNo = models.CharField(max_length= 16, blank=True, null=True)
    방향 = models.CharField(max_length= 16, blank=True, null=True)
    lat = models.CharField(max_length= 16, blank=True, null=True)
    lng = models.CharField(max_length= 16, blank=True, null=True)
    면적_평 = models.DecimalField(max_digits= 16, decimal_places= 2, blank=True, null=True)
    공급면적_평 = models.DecimalField(max_digits= 16, decimal_places= 2, blank=True, null=True)
    전용면적_평 = models.DecimalField(max_digits= 16, decimal_places= 2, blank=True, null=True)
    전용률 = models.DecimalField(max_digits= 5, decimal_places= 2, blank=True, null=True)
    층 = models.SmallIntegerField(blank=True, null=True)
    한글층 = models.CharField(max_length= 8, blank=True, null=True)
    총층 = models.SmallIntegerField(blank=True, null=True)
    point = models.IntegerField(blank=True, null=True, db_index=True)

    sido = models.CharField(max_length= 16, blank=True, null=True, db_index=True)
    sgg = models.CharField(max_length= 16, blank=True, null=True, db_index=True)
    emd = models.CharField(max_length= 16, blank=True, null=True, db_index=True)
    jb = models.CharField(max_length= 16, blank=True, null=True)
    bad_jb = models.CharField(max_length= 255, blank=True, null=True)
    juso = models.CharField(max_length= 64, blank=True, null=True)

    tagList = models.CharField(max_length= 255, blank=True, null=True)
    is_live = models.BooleanField(default=False, db_index=True)
    is_live_checked_at = models.DateTimeField(blank=True, null=True, db_index=True)

    매매가 = models.PositiveBigIntegerField(blank=True, null=True, db_index=True)
    보증금 = models.PositiveBigIntegerField(blank=True, null=True, db_index=True)
    융자금 = models.PositiveBigIntegerField(blank=True, null=True, db_index=True)
    임대료 = models.PositiveBigIntegerField(blank=True, null=True, db_index=True)
    기보증금 = models.PositiveBigIntegerField(blank=True, null=True)
    기월세 = models.PositiveBigIntegerField(blank=True, null=True)
    관리비 = models.PositiveIntegerField(blank=True, null=True)

    공급면적_평당_매매가 = models.PositiveIntegerField(blank=True, null=True)
    전용면적_평당_매매가 = models.PositiveIntegerField(blank=True, null=True)
    공급면적_평당_임대료 = models.PositiveIntegerField(blank=True, null=True)
    전용면적_평당_임대료 = models.PositiveIntegerField(blank=True, null=True)
    공급면적_평당_보증금 = models.PositiveIntegerField(blank=True, null=True)
    전용면적_평당_보증금 = models.PositiveIntegerField(blank=True, null=True)
    평당_매매가 = models.PositiveIntegerField(blank=True, null=True)
    평당_보증금 = models.PositiveIntegerField(blank=True, null=True)
    평당_임대료 = models.PositiveIntegerField(blank=True, null=True)

    난방1 = models.CharField(max_length= 16, blank=True, null=True)
    난방2 = models.CharField(max_length= 16, blank=True, null=True)
    방수 = models.PositiveSmallIntegerField(blank=True, null=True)
    욕실수 = models.PositiveSmallIntegerField(blank=True, null=True)
    총_주차대수 = models.PositiveSmallIntegerField(blank=True, null=True)
    주차가능여부 = models.BooleanField(blank=True, null=True)
    건축물_용도 = models.CharField(max_length= 16, blank=True, null=True)
    건물_주용도 = models.CharField(max_length= 16, blank=True, null=True)
    건물_총_가구 = models.PositiveSmallIntegerField(blank=True, null=True)
    대장_지역 = models.CharField(max_length= 16, blank=True, null=True)
    대장_지구 = models.CharField(max_length= 16, blank=True, null=True)
    대장_구역 = models.CharField(max_length= 16, blank=True, null=True)
    건물_사용승인일 = models.DateField(blank=True, null=True)
    건물_층정보_지하 = models.PositiveSmallIntegerField(blank=True, null=True)
    건물_층정보_지상 = models.PositiveSmallIntegerField(blank=True, null=True)
    건물_주차장_옥내 = models.PositiveSmallIntegerField(blank=True, null=True)
    건물_주차장_옥외 = models.PositiveSmallIntegerField(blank=True, null=True)
    건물_엘레베이터_비상 = models.PositiveSmallIntegerField(blank=True, null=True)
    건물_엘레베이터_승용 = models.PositiveSmallIntegerField(blank=True, null=True)
    보안시설 = models.CharField(max_length= 64, blank=True, null=True)
    기타시설 = models.CharField(max_length= 64, blank=True, null=True)
    냉방시설 = models.CharField(max_length= 64, blank=True, null=True)
    생활시설 = models.CharField(max_length= 64, blank=True, null=True)
    방범창_베란다 = models.CharField(max_length= 16, blank=True, null=True)
    상세설명 = models.TextField(blank=True, null=True)

    토지_지역 = models.CharField(max_length= 64, blank=True, null=True)
    토지_현재용도 = models.CharField(max_length= 64, blank=True, null=True)
    토지_진입도로 = models.BooleanField(blank=True, null=True)

    기타주소 = models.CharField(max_length= 255, blank=True, null=True)

    노출시작일 = models.DateField(blank=True, null=True)
    노출종료일 = models.DateField(blank=True, null=True)
    pnu = models.CharField(max_length= 32, blank=True, null=True, db_index=True)
    pnu_processed_at = models.DateTimeField(blank=True, null=True, db_index=True)
    입주타입 = models.CharField(max_length= 16, blank=True, null=True)
    입주가능일 = models.DateField(blank=True, null=True)
    현관구조 = models.CharField(max_length= 16, blank=True, null=True)
    건설사 = models.CharField(max_length= 32, blank=True, null=True)

    지하철역_갯수 = models.PositiveSmallIntegerField(blank=True, null=True)
    버스정류장_갯수 = models.PositiveSmallIntegerField(blank=True, null=True)
    지하철역_도보시간_분 = models.PositiveSmallIntegerField(blank=True, null=True)

    type1 = models.CharField(max_length= 64, blank=True, null=True)
    type2 = models.CharField(max_length= 16, blank=True, null=True)
    type3 = models.CharField(max_length= 16, blank=True, null=True)
    type4 = models.CharField(max_length= 16, blank=True, null=True)
    articleStatusCode = models.CharField(max_length= 16, blank=True, null=True)
    articleTypeCode = models.CharField(max_length= 16, blank=True, null=True)
    lawUsage = models.CharField(max_length= 32, blank=True, null=True)
    moveInDiscussionPossibleYN = models.BooleanField(blank=True, null=True)
    moveInPossibleYmd = models.DateField(blank=True, null=True)
    moveInTypeCode = models.CharField(max_length= 16, blank=True, null=True)
    parkingCount = models.PositiveSmallIntegerField(blank=True, null=True)
    parkingPossibleYN = models.BooleanField(blank=True, null=True)

    has_detail_text = models.BooleanField(default= False, db_index= True)
    detail_text = models.TextField(blank=True, null=True)
    is_detail_processed = models.BooleanField(default= False, db_index=True)
    is_detail_failed = models.BooleanField(default= False, db_index=True)
    detail_processed_at = models.DateTimeField(blank=True, null=True, db_index=True)

    has_sel_text = models.BooleanField(default= False, db_index= True)
    sel_text = models.TextField(blank=True, null=True)
    is_sel_processed = models.BooleanField(default= False, db_index=True)
    sel_processed_at = models.DateTimeField(blank=True, null=True)

    has_history = models.BooleanField(default= False, db_index= True)

    dev_memo = models.CharField(max_length= 255, blank=True, null=True)
    dev_memo2 = models.CharField(max_length= 255, blank=True, null=True)
    dev_memo3 = models.CharField(max_length= 255, blank=True, null=True)

    gijun_date = models.DateField(blank=True, null=True, db_index=True)
    gijun_date_str = models.CharField(max_length= 16, blank=True, null=True, db_index=True)

    # 230819 신규
    articleSubName = models.CharField(max_length= 64, blank=True, null=True)
    tradeCompleteYN = models.BooleanField(blank=True, null=True)
    총동갯수 = models.PositiveSmallIntegerField(blank=True, null=True)
    directTradeYN = models.BooleanField(blank=True, null=True)
    방갯수 = models.PositiveSmallIntegerField(blank=True, null=True)
    화장실갯수 = models.PositiveSmallIntegerField(blank=True, null=True)
    건물이름 = models.CharField(max_length= 32, blank=True, null=True)
    현재용도 = models.CharField(max_length= 32, blank=True, null=True)
    추천업종 = models.CharField(max_length= 32, blank=True, null=True)
    duplexYN = models.BooleanField(blank=True, null=True)
    floorLayerName = models.CharField(max_length= 32, blank=True, null=True)
    isComplex = models.BooleanField(blank=True, null=True)
    floorInfo = models.CharField(max_length= 32, blank=True, null=True)
    priceChangeState = models.CharField(max_length= 32, blank=True, null=True)
    isPriceModification = models.BooleanField(blank=True, null=True)
    cpName = models.CharField(max_length= 32, blank=True, null=True)


    class Meta:
        abstract = True

    def __str__(self):
        juso = ''
        if self.juso:
            return self.article_id + ' ' + self.juso + ' - ' + str(self.중요설명)
        else:
            return self.article_id + ' ' + self.sido + ' ' + self.sgg + ' ' + self.emd + '-' + self.중요설명


class Article서울시(ArticleBase):
    pass
class Article서울시History(ArticleBase):
    article_id = models.CharField(max_length= 16, db_index=True)
    parent = models.ForeignKey(Article서울시, on_delete=models.CASCADE, null=True, blank=True, related_name='history_set')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['article_id', 'gijun_date'],name='unique_article_id_gijun_date_서울시')]

class Article경기도(ArticleBase):
    pass
class Article경기도History(ArticleBase):
    article_id = models.CharField(max_length= 16, db_index=True)
    parent = models.ForeignKey(Article경기도, on_delete=models.CASCADE, null=True, blank=True, related_name='history_set')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['article_id', 'gijun_date'],name='unique_article_id_gijun_date_경기도')]

class Article인천시(ArticleBase):
    pass
class Article인천시History(ArticleBase):
    article_id = models.CharField(max_length= 16, db_index=True)
    parent = models.ForeignKey(Article인천시, on_delete=models.CASCADE, null=True, blank=True, related_name='history_set')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['article_id', 'gijun_date'],name='unique_article_id_gijun_date_인천시')]
