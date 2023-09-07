# BytePiece
BytePiece是一个Byte-based的Unigram分词器，纯Python实现，更加易读和易拓展。由于采用了新的训练算法，所以压缩率通常比现有Tokenizer更高，同时支持多进程加速训练。此外，它直接操作文本的UTF-8 Bytes，几乎不进行任何的预处理，所以更加纯粹和语言无关。

博客：https://kexue.fm/archives/9752

## 性质

理想的Tokenizer及其训练算法，应该具备以下特点：
- 无损重构
- 高压缩率
- 语言无关
- 数据驱动
- 训练友好

目前主流的[SentencePiece](https://github.com/google/sentencepiece)，事实上已经基本具备以上特性，但仍存在一些问题。比如：它支持BPE和Unigram两种算法，BPE压缩率往往更高一些，但训练极慢，而且非常耗内存；它还是对文本进行了少许语言相关的预处理的，所以“语言无关”这一点也不够纯粹。此外，它是用C++写的，对于多数用户来说就是黑箱，因此也不利于研究和修改。

BytePiece构思了新的基于Byte-based N-gram Language Model（BNLM）的训练方式，能获得更高压缩率的词表，同时支持多进程训练，同等语料下相比SentencePiece的BPE训练有明显的加速。代码是纯Python，方便大家阅读和二次修改。

## 原理

新的训练方式基于N-gram语言模型的新词发现算法，首次提出于笔者7年前的博客[《【中文分词系列】 5. 基于语言模型的无监督分词》](https://kexue.fm/archives/3956)。

## 安装

BytePiece使用了[pyahocorasick](https://github.com/WojciechMula/pyahocorasick)来加速训练过程。由于BytePiece是Byte-based的，而PyPi上的pyahocorasick是Unicode-based的，所以不能直接用，需要参考如下方式安装Byte-based版的pyahocorasick：
```bash
pip uninstall pyahocorasick  # 如果已经安装，请先卸载
AHOCORASICK_BYTES=1 pip install git+https://github.com/WojciechMula/pyahocorasick.git  # 直接从git编译安装，注意要传入环境变量AHOCORASICK_BYTES
```
安装完pyahocorasick之后，就可以用pip安装BytePiece了：
```bash
pip install bytepiece==0.1.0
```

## 使用

## 引用

## 交流
