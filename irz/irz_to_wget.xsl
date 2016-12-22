<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:math="http://exslt.org/math" extension-element-prefixes="math">
<xsl:output method="text"/>
<xsl:template match="/">
   <xsl:for-each select="//table[@class='list']/tr">
    <xsl:for-each select="td">
       <xsl:if test="a/@href != ''">  
        <xsl:text>wget -O </xsl:text><xsl:value-of select="substring-after(a/@href, 'id=')"/><xsl:text> "http://portal.cenia.cz/irz/</xsl:text><xsl:value-of select="a/@href"/><xsl:text>"</xsl:text>	
        <xsl:text>&#xa;</xsl:text>
        <xsl:text>sleep </xsl:text><xsl:value-of select="(floor(math:random()*10) mod 10) + 1" />
        <xsl:text>&#xa;</xsl:text>
       </xsl:if> 
    </xsl:for-each>
   </xsl:for-each>
</xsl:template>

</xsl:stylesheet>
