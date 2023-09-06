# BytePiece
BytePiece是一个bytes-based的Unigram分词器。由于采用了新的训练算法，所以压缩率通常比现有tokenizer更高。此外，它直接操作文本的utf-8 bytes，几乎不进行任何的预处理，所以更加纯粹和语言无关。

## 性质

理想的Tokenizer及其训练算法，应该具备以下特点：
- 无损重构
- 高压缩率
- 语言无关
- 数据驱动
- 训练友好

目前主流的[SentencePiece](https://github.com/google/sentencepiece)，事实上已经基本具备以上特性，但仍存在一些问题。比如：它支持bpe和unigram两种算法，bpe压缩率往往更高一些，但训练极慢，而且非常耗内存；它还是对文本进行了少许语言相关的预处理的，所以“语言无关”这一点也不够纯粹。此外，它是用C++写的，对于多数用户来说就是黑箱，因此也不利于研究和修改。

BytePiece构思了新的基于Bytes-based N-gram Language Model（BNLM）的训练方式，能获得更高压缩率的词表，同时支持多进程训练，同等语料下相比SentencePiece的bpe训练有明显的加速。代码是纯Python，方便大家阅读和二次修改。

## 原理

## 安装

## 使用

## 引用

## 交流
