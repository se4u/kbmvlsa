/**
 * Created by pushpendrerastogi on 11/12/16.
 */

import org.apache.commons.compress.utils.IOUtils;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.LowerCaseFilter;
import org.apache.lucene.analysis.StopFilter;
import org.apache.lucene.analysis.en.KStemFilter;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.analysis.standard.StandardTokenizer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.FieldType;
import org.apache.lucene.index.IndexOptions;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

import java.io.*;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.zip.GZIPInputStream;


public class BuildLuceneIndex {
    public static String createPatternString(String[] fields) {
        // <DOC>.+?<DOCNO>(.+?)</DOCNO>.+?<TITLE>(.+?)</TITLE> ... <TEXT>(.+?)</TEXT>.+?</DOC>
        StringBuilder sb = new StringBuilder();
        sb.append("<DOC>.+?");
        for (String s: fields){
            sb.append("<");
            sb.append(s);
            sb.append(">(.+?)</");
            sb.append(s);
            sb.append(">.+?");
        }
        sb.append("</DOC>");
        return sb.toString();
    }

    private static void main_impl () throws Exception {
        // String pathCorpus = "/Users/pushpendrerastogi/data/chen-xiong-EntityRankData/dbpedia.trecweb.gz";
        String pathCorpus = "/tmp/example_corpus_chen.gz";
        String pathIndex = "/tmp/example_index_lucene";

        Directory dir;
        dir = FSDirectory.open(new File(pathIndex).toPath());

        // Analyzer includes options for text processing
        Analyzer analyzer = new Analyzer() {
            @Override
            protected TokenStreamComponents createComponents(String fieldName) {
                // Step 1: tokenization (Lucene's StandardTokenizer is suitable for most text retrieval occasions)
                TokenStreamComponents ts = new TokenStreamComponents(new StandardTokenizer());
                // Step 2: transforming all tokens into lowercased ones
                ts = new TokenStreamComponents(ts.getTokenizer(), new LowerCaseFilter(ts.getTokenStream()));
                // Step 3: whether to remove stop words
                ts = new TokenStreamComponents( ts.getTokenizer(),
                        new StopFilter( ts.getTokenStream(),
                                StandardAnalyzer.ENGLISH_STOP_WORDS_SET));
                // Step 4: whether to apply stemming
                ts = new TokenStreamComponents( ts.getTokenizer(), new KStemFilter( ts.getTokenStream() ) );
                // ts = new TokenStreamComponents( ts.getTokenizer(), new PorterStemFilter( ts.getTokenStream() ) );
                return ts;
            }
        };
        // Read more about Lucene's text analysis:
        // http://lucene.apache.org/core/6_2_0/core/org/apache/lucene/analysis/package-summary.html#package.description

        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        // Note that IndexWriterConfig.OpenMode.CREATE will override the original index in the folder
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE );

        IndexWriter ixwriter = new IndexWriter(dir, config);
        // This is the field setting for normal text field.
        FieldType fieldTypeText = new FieldType();
        fieldTypeText.setIndexOptions(IndexOptions.DOCS_AND_FREQS);
        fieldTypeText.setStoreTermVectors(true);
        fieldTypeText.setOmitNorms(false);
        fieldTypeText.setTokenized(true);
        fieldTypeText.setStored(true);
        fieldTypeText.freeze();

        // Iteratively read each document from the corpus file,
        // create a Document object for the parsed document, and add that
        // Document object by calling addDocument().
        String[] patFields = {"DOCNO", "DOCHDR", "names", "category", "attributes", "SimEn", "RelEn"};
        String[] patFieldsLower = new String[patFields.length];
        for (int i = 0; i < patFields.length; i++){
            patFieldsLower[i] = patFields[i].toLowerCase();
        }
        Pattern pattern = Pattern.compile(
                createPatternString(patFields),
                Pattern.CASE_INSENSITIVE + Pattern.MULTILINE + Pattern.DOTALL
        );

        InputStream instream = new GZIPInputStream(new FileInputStream(pathCorpus));
        Scanner scanner = new Scanner(instream);
        String tmp;
        int counter = 0;
        while(scanner.hasNext())
        {
            tmp = scanner.findWithinHorizon(pattern, 0);
            if(tmp == null) break;
            // System.out.println(tmp);
            Matcher matcher = pattern.matcher(tmp);
            matcher.matches();
            // Create a Document object
            Document d = new Document();
            for (int i=0; i < patFields.length; i++){
                String data = matcher.group(i).trim();
                d.add(new Field(patFieldsLower[i], data, fieldTypeText));
            }
            // Add the document to index.
            ixwriter.addDocument(d);
            if (counter % 300000 == 0){
                System.out.println(counter);
            }
            counter += 1;
        }
        // Close the file, the index writer and the directory
        instream.close();
        ixwriter.close();
        dir.close();
    }
    public static void main (String [] args){
        try {
            main_impl();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}